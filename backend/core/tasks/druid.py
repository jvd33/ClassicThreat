import asyncio
import ujson
import aiohttp
import logging

from urllib.parse import urlparse
from typing import List
from fastapi import HTTPException
from collections import defaultdict

from ..models.common import WCLDataRequest, BossActivityRequest
from ..models.druid import DruidThreatCalculationRequest, DruidThreatResult, DruidDamageResponse, DruidCastResponse, ShapeshiftEvent
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
    async def __recalculate_opts(data, req=req):
        data['feral_instinct_points'] = req.feral_instinct_points
        data['friendlies_in_combat'] = req.friendlies_in_combat
        data['no_bear'] = ujson.loads(data['no_bear'])
        r = DruidThreatCalculationRequest(**data)
        return r.calculate_druid_threat(cached=True)

    logger.info(f'REQUEST FOR: {req.player_name} -------- REPORT: {req.url} -------- BOSSES: {req.bosses}')
    report_id = req.report_id
    missing = req.bosses
    cache_resp = {}
    
    try:
        redis = RedisClient()
        cached_data = await redis.check_cache(report_id, req.player_name, req.bosses, db=1) or {}
        if cached_data.get('matches'):
            cache_resp = {k: await __recalculate_opts(v) for k, v in cached_data.get('matches').items()}
        missing = cached_data.get('missing', [])
    except Exception as exc:
        logger.error(f'Failed to read from cache {exc}')
    
    wcl = WCLService(session=session)
    resp = await wcl.get_full_report(report_id)
    missing = set(req.bosses) - set(cache_resp.keys()) if req.bosses else \
                    set([v.get('name') for v in resp.get('fights') if v.get('boss') != 0 and v.get('kill') == True]) - set(cache_resp.keys()) 
    bosses = [v for v in resp.get('fights') if v.get('name') in missing and v.get('boss') != 0]
    
    if not bosses:
        if not cache_resp:
            logger.error(f'No bosses found in log {report_id} OR cache for player {req.player_name}: {bosses}')
            raise HTTPException(status_code=404,
                                detail=f'Not found: No boss activity found matching {req.bosses}')
        ranks = {k: v for k, v in sorted(cache_resp.items(), key=lambda x: x[1].get('boss_id'))}
        for k, v in ranks.items():
            try:
                rank = await redis.get_encounter_percentile(k, v.get('tps'), db=3)
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
    ) for boss in bosses]

    d = await get_player_activity(player_name, player_cls, realm, reqs, req.feral_instinct_points, req.friendlies_in_combat, session) or {}
    events = await get_events(player_name, player_cls, realm, reqs, req.feral_instinct_points, req.friendlies_in_combat, session)
    ranks = {k: v for k, v in sorted({**d, **cache_resp}.items(), key=lambda x: x[1].get('boss_id'))}
    for k, v in ranks.items():
        try:
            rank = await redis.get_encounter_percentile(k, v.get('tps'), db=3)
            v.update({'rank': rank})
        except Exception as exc:
            logger.error(f'Failed to write to read from cache {exc}')
    return ranks, events
 
async def get_player_activity(player_name, player_class, realm, reqs: List[BossActivityRequest], fi_pts, friendlies, session):
    if not reqs:
        return []
    wcl = WCLService(session=session)
    report_id = reqs[0].report_id if reqs[0] else None
    shift_events = await asyncio.gather(*[wcl.get_stance_state(req) for req in reqs])
    shifts = [await process_shapeshifts(e) for e in shift_events]
    futures = [asyncio.gather(*[wcl.get_fight_details(req, event) for event in EVENTS]) for req in reqs]
    future_results = await asyncio.gather(*futures)
    results = []

    for fight in future_results:
        resp = {}
        no_bear_resp = {}
        for data in fight:
            form = [shift for shift in shifts if shift.get('boss_name') == data.get('boss_name')]
            if data.get('totalTime', None):
                resp['time'] = data.get('totalTime') / 1000.0
            bear, nobear = await process_data_response(data.get('event'))(data, form)
            no_bear_resp.update(**dict(nobear), boss_name=data.get('boss_name'), boss_id=data.get('boss_id'), friendlies_in_combat=friendlies)
            resp.update(**dict(bear), boss_name=data.get('boss_name'), boss_id=data.get('boss_id'))
        resp['enemies_in_combat'] = resp.get('enemies_in_combat', 0) or 1
        nobear['enemies_in_combat'] = nobear.get('enemies_in_combat', 0) or 1
        r = DruidThreatCalculationRequest(**resp,
                                            player_name=player_name,
                                            player_class=player_class,
                                            realm=realm,
                                            feral_instinct_points=fi_pts,
                                            friendlies_in_combat=friendlies,
                                            no_bear=no_bear_resp
                                            )
        tps = r.calculate_druid_threat()
        results.append(tps)
    ret_json = {result.get('boss_name'): {k: v for k, v in sorted(result.items(), key=lambda x: x[0])} for result in results}
    try:
        redis = RedisClient()
        await redis.save_druid_results(report_id, player_name, ret_json)
    except Exception as exc:
        logger.error(f'Failed to write to cache {exc}')
    return ret_json


async def get_events(player_name, player_class, realm, reqs: List[BossActivityRequest], def_pts, friendlies, t1, session):
    if not reqs:
        return []
    wcl = WCLService(session=session)
    report_id = reqs[0].report_id if reqs[0] else None
    stance_events = await asyncio.gather(*[wcl.get_stance_state(req) for req in reqs])
    stances = [await process_stance_state(e) for e in stance_events]
    futures = [asyncio.gather(*[wcl.get_fight_details(req, event) for event in EVENTS]) for req in reqs]
    future_results = await asyncio.gather(*futures)
    all_events = defaultdict(str, defaultdict(str))
    for fight in future_results:
        for data in fight:
            all_events[data.get('boss_name')].get('events', []).extend(data.get('events'))
            all_events[data.get('boss_name')]['total_time'] = data.get('total_time')
            stance = [stance for stance in stances if stance.get('boss_name') == data.get('boss_name')]

            dstance, nostance = await process_data_response(data.get('event'))(data, stance)

    try:
        redis = RedisClient()
        await redis.save_events(report_id, player_name, all_events)
    except Exception as exc:
        logger.error(f'Failed to write to cache {exc}')
    all_events = {
        k: FightLog.from_response(v.get('events'), report_id, player_name, k, v.get('total_time')) 
        for k, v in all_events.items()
    }
    return all_events

def process_data_response(request_type):
    return {
        'damage-done': process_damage_done,
        'casts': process_casts,
        'resources-gains': process_rage_gains,
        'healing': process_healing_done,
        'debuffs': process_debuffs,
        'stance': process_shapeshifts,
    }.get(request_type)


async def process_damage_done(data, shapeshift_events):

    __flat = {
        Spell.Maul: 'maul_hits',
        Spell.Swipe: 'swipe_hits',
    }
    add_count = set()
    damage_entries = data.get('events')
    hits = DruidDamageResponse()
    no_bear = DruidDamageResponse()
    if not damage_entries:
        # Return 0 for damage or set the equivalent, dunno yet haven't gotten that far
        return hits, no_bear

    shifts = shapeshift_events[0] or {}
    for entry in damage_entries:
        add_count.add(str(entry.get('targetID')) + ':' + str(entry.get('targetInstance')))
        form = _get_event_stance(shifts, entry, hits, no_bear)
        form.enemies_in_combat = len(add_count)

        guid = entry.get('ability').get('guid')
        if guid == Spell.Maul and entry.get('hitType') not in [7, 8]:
            form.maul_dmg += (entry.get('amount', 0) + entry.get('absorbed', 0))
        elif guid == Spell.Swipe and entry.get('hitType') not in [7, 8]:
            form.swipe_dmg += (entry.get('amount', 0) + entry.get('absorbed', 0))
        elif guid in __flat.keys() and entry.get('hitType') not in [7, 8]:
            setattr(form, __flat[guid], getattr(form, __flat[guid]) + 1)
            form.total_damage += (entry.get('amount', 0) + entry.get('absorbed', 0))
        else:
            form.total_damage += (entry.get('amount') + entry.get('absorbed', 0))
    return hits, no_bear


async def process_rage_gains(data, shapeshift_events):
    rage_gains = data.get('resources', [])
    rage_gain_events = [r.get('gains') for r in rage_gains]
    return {'rage_gains': sum(rage_gain_events)}, ShapeshiftEvent()


async def process_healing_done(data, shapeshift_events):
    healing_entries = data.get('entries')
    if not healing_entries:
        return {'hp_gains': 0}, ShapeshiftEvent()
    healing_events = [event.get('total') for event in healing_entries]
    return {'hp_gains': sum(healing_events)}, ShapeshiftEvent()


async def process_casts(data, shift_events):
    cast_entries = data.get('events')
    shapeshifts = shift_events[0] or {}
    resp = DruidCastResponse()
    no_bear = DruidCastResponse()
    if not cast_entries:
        return resp, no_bear # All 0 default vals

    abilities = {
        Spell.DemoRoar: 'demo_casts',
        Spell.Maul: 'maul_casts',
        Spell.Swipe: 'swipe_casts',
        Spell.Cower: 'cower_casts',
        Spell.FaerieFireFeral: 'ff_hits',
        Spell.FaerieFire: 'ff_hits'
    }

    for entry in [e for e in cast_entries if e.get('ability').get('guid') in abilities]:
        form = _get_event_stance(shapeshifts, entry, resp, no_bear)
        guid = entry.get('ability').get('guid')
        resp_attr = abilities.get(guid)
        setattr(form, resp_attr, getattr(form, resp_attr) + 1)
    return resp, no_bear


async def process_debuffs(data, shapeshift_events):
    goa_procs = [d for d in data.get('events') if d.get('ability').get('guid') == Spell.GiftOfArthas]
    bear = defaultdict(int)
    no_bear = defaultdict(int)
    shapeshifts = shapeshift_events[0] or {}

    for proc in goa_procs:
        if proc.get('type') == 'applydebuff' or proc.get('type') == 'refreshdebuff':
            form = _get_event_stance(shapeshifts, proc, bear, no_bear)
            form['goa_procs'] += 1
    return bear, no_bear


async def process_shapeshifts(data):
    forms = [Spell.CatForm, Spell.BearForm]
    entries = [e for e in data.get('events') if e.get('ability').get('guid') in forms]
    windows = {
        Spell.BearForm: [],
        Spell.CatForm: []
    }
    time = data.get('start_time')
    last_form = Spell.BearForm
    for e in entries:
        if e.get('type') == 'removebuff':
            windows[e.get('ability').get('guid')].append((time, e.get('timestamp')))
        if e.get('type') == 'applybuff':
            time = e.get('timestamp')
            last_form = e.get('ability').get('guid')

    if last_form:
        windows[last_form].append((time, 0))
    return {**windows, 'boss_name': data.get('boss_name')}


def _get_event_stance(shapeshift_events, event, bear, nobear):
    time = event.get('timestamp')
    for k, rnges in [el for el in shapeshift_events.items() if el[0] != 'boss_name']:
        for rnge in rnges:
            if rnge[0] <= time and (time <= rnge[1] if rnge[1] else True):
                return nobear if k != Spell.BearForm else bear
    return bear
