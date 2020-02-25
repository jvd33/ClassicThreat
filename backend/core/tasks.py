import asyncio
import ujson
import aiohttp
import logging

from urllib.parse import urlparse
from typing import List
from fastapi import HTTPException
from collections import defaultdict

from .models.common import WCLDataRequest, BossActivityRequest, FightLog
from .models.warrior import WarriorThreatCalculationRequest, WarriorThreatResult
from .models.druid import DruidThreatCalculationRequest, DruidThreatResult
from .models.paladin import PaladinThreatCalculationRequest, PaladinThreatResult
from .constants import Spell
from .wcl_service import WCLService
from .cache import RedisClient
from .utils import flatten


logger = logging.getLogger()

def __warr_recalc_opts(logs, req):
    for log in logs:
        log['defiance_points'] = req.talent_pts
        log['t1_set'] = req.t1_set
        log['friendlies_in_combat'] = req.friendlies_in_combat
        yield WarriorThreatCalculationRequest.from_event_log(FightLog(**log))

def __druid_recalc_opts(logs, req):
    for log in logs:
        log['feral_instinct_points'] = req.talent_pts
        log['friendlies_in_combat'] = req.friendlies_in_combat
        yield DruidThreatCalculationRequest.from_event_log(FightLog(**log))

def __paladin_recalc_opts(logs, req):
    for log in logs:
        log['imp_rf_points'] = req.talent_pts
        log['friendlies_in_combat'] = req.friendlies_in_combat
        yield PaladinThreatCalculationRequest.from_event_log(FightLog(**log))

def get_class_opts(player_class):
    return {
        'warrior': [0, WarriorThreatCalculationRequest, __warr_recalc_opts, 'save_warr_results', 2],
        'druid': [1, DruidThreatCalculationRequest, __druid_recalc_opts, 'save_druid_results', 3],
        'paladin': [5, PaladinThreatCalculationRequest, __paladin_recalc_opts, 'save_paladin_results', 6]
    }.get(player_class, None)

async def get_log_data(req: WCLDataRequest, session, player_class):
    """
    TODO: Refactor this so the cache logic is separated from the external API call logic
    This is too much and it makes it impossible to reuse the calculation code
    """

    logger.info(f'REQUEST FOR: {req.player_name} -------- REPORT: {req.url} -------- BOSSES: {req.bosses}')
    report_id = req.report_id
    missing = req.bosses
    cache_resp = {}
    data_db, calc_model, recalc_fn, save, rank_db = get_class_opts(player_class)    

    try:
        redis = RedisClient()
        cached_data = await redis.check_cache(report_id, req.player_name, req.bosses, db=data_db) or {}
        if cached_data.get('matches'):
            cache_resp = {}
            for k in cached_data.get('matches'):
                logs = {} #await redis.get_events(report_id, req.player_name, bosses=[k])
                if logs:
                    result = recalc_fn(logs, req=req)
                    cache_resp.update(**{
                        r.boss_id: r.dict() for r in result
                    })
                    await getattr(redis, save)(report_id, req.player_name, cache_resp)
        missing = cached_data.get('missing', [])
    except Exception as exc:
        logger.error(f'Failed to read historic records from cache {exc}')
    
    wcl = WCLService(session=session)
    resp = await wcl.get_full_report(report_id)
    missing = set(req.bosses) - set(cache_resp.keys()) if req.bosses else \
                    set([v.get('name') for v in resp.get('fights') if v.get('boss') != 0]) - set(cache_resp.keys()) 
    bosses = [v for v in resp.get('fights') if v.get('name') in missing and v.get('boss') != 0]
    
    if not req.include_wipes:
        bosses = [b for b in bosses if b.get('kill') == 1]
        
    if not bosses:
        if not cache_resp:
            logger.error(f'No bosses found in log {report_id} OR cache for player {req.player_name}: {bosses}')
            raise HTTPException(status_code=404,
                                detail=f'Not found: No boss activity found matching {req.bosses}')
        ranks = {k: v for k, v in sorted(cache_resp.items(), key=lambda x: x[1].get('boss_id'))}
        ret = {}
        count = defaultdict(lambda:1)
        for k, v in ranks.items():
            boss_name = v.get('boss_name')
            try:
                rank = await redis.get_encounter_percentile(boss_name, v.get('modified_tps'), db=rank_db)
                v.update({'rank': rank})
            except Exception as exc:
                logger.error(f'Failed to read {k} percentiles from cache {exc}')
            finally:
                if v.get('is_kill', False):
                    ret[boss_name] = v
                else:
                    wipe_count = count.get(boss_name, 1)
                    entry_name = f'{boss_name} Wipe {wipe_count}'
                    ret[entry_name] = v
                    count[boss_name] += 1
        return ranks, cache_resp
    
    bosses = list(filter(lambda x: x.get('name') in [*req.bosses, *missing], bosses)) or bosses
    player_info = [p for p in resp.get('friendlies') if p.get('name').casefold() == req.player_name.casefold()]
    if not player_info:
        logger.error(f'Player {req.player_name} not found in provided report {report_id}.')
        raise HTTPException(status_code=404,
                            detail=f'Not found: No player named {req.player_name} found in the linked log.')

    player_info = player_info[0]
    player_name = player_info.get('name')
    player_cls = player_info.get('type')
    if player_cls.casefold() != player_class.casefold():
        raise HTTPException(status_code=400,
                    detail=f'Bad Request: Player {req.player_name} was found in the linked log, \
                    but is class {player_cls}. Use the correct calculator.')
    realm = player_info.get('server')
    del player_info['fights']
    
    reqs = [BossActivityRequest(
        player_id=player_info.get('id'),
        start_time=boss.get('start_time'),
        end_time=boss.get('end_time'),
        encounter=boss.get('id'),
        boss_name=boss.get('name'),
        report_id=report_id,
        is_kill=boss.get('kill')
    ) for boss in bosses]

    events = await get_events(player_name, player_cls, realm, reqs, req.talent_pts, req.friendlies_in_combat, session, req.t1_set)

    r = [calc_model.from_event_log(log) for boss, log in events.items()]
    r = {
        a.boss_id: a.dict() for a in r
    }

    try:
        redis = RedisClient()
        await getattr(redis, save)(report_id, player_name, r)
    except Exception as exc:
        logger.error(f'Failed to write cache {report_id}:{player_name}, {exc}')

    ranks = {k: v for k, v in sorted({**r, **cache_resp}.items(), key=lambda x: x[1].get('boss_id'))}

    ret = {}
    count = defaultdict(lambda:1)
    for k, v in ranks.items():
        boss_name = v.get('boss_name')
        try:
            rank = await redis.get_encounter_percentile(boss_name, v.get('modified_tps'), db=rank_db)
            v.update({'rank': rank})
        except Exception as exc:
            logger.error(f'Failed to read {boss_name}, {k} percentiles from cache {exc}')
        finally:
            if v.get('is_kill', False):
                ret[boss_name] = v
            else:
                wipe_count = count.get(boss_name, 1)
                entry_name = f'{boss_name} Wipe {wipe_count}'
                ret[entry_name] = v
                count[boss_name] += 1
    return ret, events
 

async def get_events(player_name, player_class, realm, reqs: List[BossActivityRequest], talent_pts, friendlies, session, t1=False):
    modifier_fn = {
        'druid': process_shapeshifts,
        'warrior': process_stance_state,
        'paladin': dummy_process_paladin_state 
    }.get(player_class.casefold(), None)
    if not modifier_fn:
        raise HTTPException(status_code=400,
                detail=f'Bad Request: {player_class} is invalid.')
    if not reqs:
        return []
    wcl = WCLService(session=session)
    report_id = reqs[0].report_id if reqs[0] else None
    future_results = await asyncio.gather(*[wcl.get_fight_details(req) for req in reqs])
    stances = [await modifier_fn(e, reqs[0].player_id) for e in future_results]
    all_events = []
    dps = await asyncio.gather(*[wcl.get_dps_details(req) for req in reqs])
    aggro_windows = await asyncio.gather(*[wcl.get_aggro_windows(req) for req in reqs])
    for fight, req in zip(future_results, reqs):
        if not fight.get('events'):
            continue
        boss = {
            'events': [],
            'total_time': fight.get('total_time'),
            'boss_name': fight.get('boss_name'),
            'start_time': fight.get('start_time'),
            'end_time': 0,
            'dps_threat': [],
            'player_gear': [],
            'boss_id': fight.get('boss_id'),
            'is_kill': bool(req.is_kill)
            
        }
        
        windows = [x for x in aggro_windows if x.get('boss_id') == fight.get('boss_id')]
        window = windows[0] if windows else None
        dps_results = [x for x in dps if x and x[0].get('boss_id') == fight.get('boss_id')]
        for b in dps_results:
            for d in b: 
                if d.get('gear'):
                    del d['gear']

        boss['dps_threat'] = dps_results[0]
        player_gear = []
        for data in fight.get('events'):
            if data.get('type') == 'combatantinfo':
                boss['gear'] = data.get('gear')
                continue 
            elif data.get('sourceID') != fight.get('player_id') and (data.get('targetID') != fight.get('player_id') or data.get('type') != 'energize') or \
                        data.get('type') not in ['cast', 'applydebuff', 'damage', 'heal', 'energize', 'refreshdebuff', 'applybuff', 'refreshbuff']:
                continue
                
            for item in player_gear:
                try:
                    del item['itemLevel']
                    del item['icon']
                    del item['quality']
                except KeyError:
                    continue
            
            boss.update(**{
                'events': [data, *boss['events']],
                'end_time': data.get('end_time'),
                'aggro_windows': window,
            })
        all_events.append(boss)
    
    all_events = {
        e.get('boss_id'): {
            'events': e.get('events'),
            'total_time': e.get('total_time'),
            'start_time': e.get('start_time'),
            'end_time': e.get('end_time'),
            'dps_threat': e.get('dps_threat'),
            'boss_name': e.get('boss_name'),
            'gear': e.get('gear'),
            'is_kill': e.get('is_kill'),
            'aggro_windows': e.get('aggro_windows'),
        } for e in all_events
    }
    all_events = {
        k: FightLog.from_response(
            resp=v.get('events'), 
            report_id=report_id, 
            player_name=player_name, 
            boss_name=v.get('boss_name'), 
            boss_id=k,
            is_kill=v.get('is_kill'),
            total_time=v.get('total_time'), 
            player_class=player_class,
            modifier_events=stances,
            dps_threat=v.get('dps_threat'),
            realm=realm,
            t1=t1,
            gear=v.get('gear'),
            talent_pts=talent_pts,
            friendlies=friendlies,
            aggro_windows=v.get('aggro_windows') or {},
        ) 
        for k, v in sorted(all_events.items(), key=lambda x: x[1].get('start_time'))
    }

    try:
        redis = RedisClient()
        await redis.save_events(report_id, player_name, all_events)
    except Exception as exc:
        logger.error(f'Failed to write to cache {exc}')

    return all_events

async def dummy_process_paladin_state(data, player_id):
    windows = {
        Spell.RighteousFury: [],
    }
    events = [e for e in data.get('events') if e.get('type') != 'combatantinfo' and e.get('sourceID') == player_id]
    if not events:
        return windows
    entries = [e for e in events if e.get('ability').get('guid') == Spell.RighteousFury]

    time = data.get('start_time')
    for e in entries:
        if e.get('type') == 'removebuff':
            windows[e.get('ability').get('guid')].append((time, e.get('timestamp')))
        if e.get('type') == 'applybuff':
            time = e.get('timestamp')
    
    windows[Spell.RighteousFury].append((time, 0))
    return {**windows, 'boss_id': data.get('boss_id')}

async def process_stance_state(data, player_id):
    windows = {
        Spell.DefensiveStance: [],
        Spell.BattleStance: [],
        Spell.BerserkerStance: []
    }
    stances = [Spell.DefensiveStance, Spell.BerserkerStance, Spell.BattleStance]
    events = [e for e in data.get('events') if e.get('type') != 'combatantinfo' and e.get('sourceID') == player_id]
    if not events:
        return windows
    entries = [e for e in events if e.get('ability').get('guid') in stances]
    zerk_specific = [
        e.get('timestamp') for e in events if e.get('ability').get('guid') in 
        [Spell.BerserkerRage, Spell.Intercept, Spell.Pummel, Spell.Recklessness, Spell.Whirlwind]
    ]
    battle_specific = [
        e.get('timestamp') for e in events if e.get('ability').get('guid') in 
        [Spell.Overpower, Spell.Charge, Spell.Retaliation, Spell.MockingBlow, Spell.ThunderClap]
    ]
    defensive_specific = [
        e.get('timestamp') for e in events if e.get('ability').get('guid') in 
        [Spell.ShieldWall, Spell.ShieldBlock, Spell.Revenge5, Spell.Revenge6, Spell.Taunt, Spell.Disarm,]
    ]
    time = data.get('start_time')
    last_stance = None
    for e in entries:
        if e.get('type') == 'removebuff' and e.get('guid') in stances:
            windows[e.get('ability').get('guid')].append((time, e.get('timestamp')))
        if e.get('type') == 'applybuff' in stances:
            time = e.get('timestamp')
            last_stance = e.get('ability').get('guid')
    
    if not last_stance:
        last_timestamp = sorted([*zerk_specific, *battle_specific, *defensive_specific], reverse=True)
        if last_timestamp and last_timestamp[0] in zerk_specific: 
            last_stance = Spell.BerserkerStance
        elif last_timestamp and last_timestamp[0] in battle_specific:
            last_stance = Spell.BattleStance
        else:
            last_stance = Spell.DefensiveStance
    windows[last_stance].append((time, 0))
    return {**windows, 'boss_id': data.get('boss_id')}


async def process_shapeshifts(data, player_id):
    windows = {
        Spell.BearForm: [],
        Spell.CatForm: [],
        Spell.HumanoidForm: []
    }
    events = [e for e in data.get('events') if e.get('type') != 'combatantinfo' and e.get('sourceID') == player_id]
    if not events:
        return windows
    forms = [Spell.CatForm, Spell.BearForm]
    entries = [e for e in events if e.get('ability').get('guid') in forms]
    

    bear_specific = [
        e for e in events if e.get('ability').get('guid') in 
        [Spell.Swipe, Spell.Maul, Spell.DemoRoar, Spell.FrenziedRegen,]
    ]
    cat_specific = [
        e for e in events if e.get('ability').get('guid') in 
        [Spell.Shred, Spell.Rake, *Spell.FerociousBite, Spell.Cower]
    ]
    caster_specific = [
        e for e in events if e.get('ability').get('guid') in 
        [*Spell.Regrowth, *Spell.Rejuvenation, *Spell.HealingTouch, *Spell.Moonfire, *Spell.Starfire, *Spell.Wrath,]
    ]

    time = data.get('start_time')
    last_form = None
    for e in entries:
        if e.get('type') == 'removebuff':
            windows[e.get('ability').get('guid')].append((time, e.get('timestamp')))
        if e.get('type') == 'applybuff':
            time = e.get('timestamp')
            last_form = e.get('ability').get('guid')
    
    if not last_form:
        if bear_specific: 
            last_form = Spell.BearForm
        elif cat_specific:
            last_form = Spell.CatForm
        elif caster_specific:
            last_form = Spell.HumanoidForm

    windows[last_form].append((time, 0))

    return {**windows, 'boss_id': data.get('boss_id')}
