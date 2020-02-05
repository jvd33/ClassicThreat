import asyncio
import ujson
import aiohttp
import logging

from urllib.parse import urlparse
from typing import List
from fastapi import HTTPException
from collections import defaultdict

from ..models.common import WCLDataRequest, BossActivityRequest, FightLog, ThreatEvent
from ..models.druid import DruidThreatCalculationRequest, DruidThreatResult
from ..constants import Spell
from ..wcl_service import WCLService
from ..cache import RedisClient
from ..utils import flatten

EVENTS = ['damage-done', 'casts', 'resources-gains', 'healing', 'debuffs']

logger = logging.getLogger()

async def get_log_data(req: WCLDataRequest, session):
    """TODO Warning: Here be dragons
    this is a prototype that got out of hand
    the caching logic can definitely be separated out and error handling can be more consistent
    """
    async def __recalculate_opts(log, req=req):
        log['feral_instinct_points'] = req.feral_instinct_points
        log['friendlies_in_combat'] = req.friendlies_in_combat
        log['dps_threat'] = log.get('dps_threat')
        log['gear'] = log.get('gear')
        return DruidThreatCalculationRequest.from_event_log(FightLog(**log))

    logger.info(f'REQUEST FOR: {req.player_name} -------- REPORT: {req.url} -------- BOSSES: {req.bosses}')
    report_id = req.report_id
    missing = req.bosses
    cache_resp = {}
    
    try:
        redis = RedisClient()
        cached_data = await redis.check_cache(report_id, req.player_name, req.bosses, db=0) or {}
        if cached_data.get('matches'):
            cache_resp = {}
            for k, v in cached_data.get('matches').items():
                log = await redis.get_events(report_id, req.player_name, bosses=[k])
                if log:
                    result = await __recalculate_opts(log, req=req)
                    cache_resp[k] = result
                    redis.save_warr_results(report_id, req.player_name, result)
        missing = cached_data.get('missing', [])
    except Exception as exc:
        logger.error(f'Failed to read from cache {exc}')
    
    wcl = WCLService(session=session)
    resp = await wcl.get_full_report(report_id)
    missing = set(req.bosses) - set(cache_resp.keys()) if req.bosses else \
                    set([v.get('name') for v in resp.get('fights') if v.get('boss') != 0 and v.get('kill') == True]) - set(cache_resp.keys()) 
    bosses = [v for v in resp.get('fights') if v.get('name') in missing and v.get('boss') != 0 and v.get('kill') == True]
    
    if not bosses:
        if not cache_resp:
            logger.error(f'No bosses found in log {report_id} OR cache for player {req.player_name}: {bosses}')
            raise HTTPException(status_code=404,
                                detail=f'Not found: No boss activity found matching {req.bosses}')
        ranks = {k: v for k, v in sorted(cache_resp.items(), key=lambda x: x[1].get('boss_id'))}
        for k, v in ranks.items():
            try:
                rank = await redis.get_encounter_percentile(k, v.get('tps'))
                v.update({'rank': rank})
            except Exception as exc:
                logger.error(f'Failed to write to read from cache {exc}')
        return ranks
    
    bosses = list(filter(lambda x: x.get('name') in [*req.bosses, *missing], bosses)) or bosses
    player_info = [p for p in resp.get('friendlies') if p.get('name').casefold() == req.player_name.casefold()]
    if not player_info:
        logger.error(f'Player {req.player_name} not found in provided report {report_id}.')
        raise HTTPException(status_code=404,
                            detail=f'Not found: No player named {req.player_name} found in the linked log.')

    player_info = player_info[0]
    player_name = player_info.get('name')
    player_cls = player_info.get('type')
    realm = player_info.get('server')
    del player_info['fights']
    
    reqs = [BossActivityRequest(
        player_id=player_info.get('id'),
        start_time=boss.get('start_time'),
        end_time=boss.get('end_time'),
        encounter=boss.get('id'),
        boss_name=boss.get('name'),
        report_id=report_id,
    ) for boss in bosses if boss.get('start_time') and boss.get('end_time')]

    events = await get_events(player_name, player_cls, realm, reqs, req.feral_instinct_points, req.friendlies_in_combat, session)

    r = [DruidThreatCalculationRequest.from_event_log(log) for boss, log in events.items()]

    r = {
        a.boss_name: a.dict() for a in r
    }

    try:
        redis = RedisClient()
        await redis.save_druid_results(report_id, player_name, r)
    except Exception as exc:
        logger.error(f'Failed to write to cache {exc}')

    ranks = {k: v for k, v in sorted({**r, **cache_resp}.items(), key=lambda x: x[1].get('boss_id'))}

    for k, v in ranks.items():
        try:
            rank = await redis.get_encounter_percentile(k, v.get('tps'))
            v.update({'rank': rank})
        except Exception as exc:
            logger.error(f'Failed to read from cache {exc}')
    return ranks, events
 
async def get_events(player_name, player_class, realm, reqs: List[BossActivityRequest], fi_pts, friendlies, session):
    if not reqs:
        return []
    wcl = WCLService(session=session)
    report_id = reqs[0].report_id if reqs[0] else None
    future_results = await asyncio.gather(*[wcl.get_fight_details(req) for req in reqs])
    stances = [await process_shapeshifts(e) for e in future_results]

    all_events = []
    dps = await asyncio.gather(*[wcl.get_dps_details(req) for req in reqs])
    for fight in future_results:
        if not fight.get('events'):
            continue
        boss = {
            'events': [],
            'total_time': 0,
            'boss_name': '',
            'start_time': 0,
            'end_time': 0,
        }
        player_gear = []
        dps_results = [x for x in dps if x[0] and x[0].get('boss_name') == fight.get('boss_name')]

        for data in fight.get('events'):
            if data.get('type') == 'combatantinfo':
                player_gear = data.get('gear')

            if data.get('sourceID') != fight.get('player_id') or data.get('type') not in ['cast', 'applydebuff', 'damage', 'heal', 'energize', 'refreshdebuff']:
                continue

            for b in dps_results:
                for d in b: 
                    if d.get('gear'):
                        del d['gear']
                
            for item in player_gear:
                try:
                    del item['itemLevel']
                    del item['icon']
                    del item['quality']
                except KeyError:
                    continue
            boss.update(**{
                'events': [data, *boss['events']],
                'total_time': fight.get('total_time'),
                'boss_name': fight.get('boss_name'),
                'start_time': fight.get('start_time'),
                'end_time': data.get('end_time'),
                'dps_threat': dps_results[0],
                'boss_id': fight.get('boss_id'),
                'gear': player_gear,
                
            })
        all_events.append(boss)
 
    all_events = {
        e.get('boss_name'): {
            'events': e.get('events'),
            'total_time': e.get('total_time'),
            'start_time': e.get('start_time'),
            'end_time': e.get('end_time'),
            'dps_threat': e.get('dps_threat'),
            'boss_id': e.get('boss_id'),
            'gear': e.get('gear')
        } for e in all_events
    }

    all_events = {
        k: FightLog.from_response(
            resp=v.get('events'), 
            report_id=report_id, 
            player_name=player_name, 
            boss_name=k, 
            boss_id=v.get('boss_id'),
            total_time=v.get('total_time'), 
            player_class=player_class,
            modifier_events=stances,
            dps_threat=v.get('dps_threat'),
            realm=realm,
            gear=v.get('gear'),
            talent_pts=fi_pts,
            friendlies=friendlies
        ) 
        for k, v in sorted(all_events.items(), key=lambda x: x[1].get('start_time'))
    }

    try:
        redis = RedisClient()
        await redis.save_events(report_id, player_name, all_events)
    except Exception as exc:
        logger.error(f'Failed to write to cache {exc}')

    return all_events


async def process_shapeshifts(data):
    windows = {
        Spell.BearForm: [],
        Spell.CatForm: [],
        Spell.HumanoidForm: []
    }
    events = [e for e in data.get('events') if e.get('type') != 'combatantinfo']
    if not events:
        return windows
    forms = [Spell.CatForm, Spell.BearForm]
    entries = [e for e in events if e.get('ability').get('guid') in forms]


    bear_specific = [
        e for e in events if e.get('ability').get('name') in 
        ['Swipe', 'Maul', 'Demoralizing Roar', 'Frenzied Regeneration',]
    ]
    cat_specific = [
        e for e in events if e.get('ability').get('name') in 
        ['Shred', 'Rake', 'Cower', 'Ferocious Bite']
    ]
    caster_specific = [
        e for e in events if e.get('ability').get('name') in 
        ['Regrowth', 'Rejuvenation', 'Faerie Fire', 'Healing Touch']
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

    return {**windows, 'boss_name': data.get('boss_name')}