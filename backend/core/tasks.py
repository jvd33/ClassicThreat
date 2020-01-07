import asyncio
import ujson

from urllib.parse import urlparse
from typing import List
from fastapi import HTTPException

from .models import WCLDataRequest, BossActivityRequest, WarriorCastResponse, \
    WarriorDamageResponse, WarriorThreatCalculationRequest
from .wcl_service import WCLService
from .cache import RedisClient

EVENTS = ['damage-done', 'casts', 'resources-gains', 'healing', 'debuffs']


async def get_log_data(req: WCLDataRequest):
    """TODO Warning: Here be dragons
    this is a prototype that got out of hand
    the caching logic can definitely be separated out and error handling can be more consistent
    """
    def __recalculate_opts(data, req=req):
        data['defiance_points'] = req.defiance_points
        data['t1_set'] = req.t1_set
        data['enemies_in_combat'] = req.enemies_in_combat
        data['friendlies_in_combat'] = req.friendlies_in_combat
        r = WarriorThreatCalculationRequest(**data)
        return r.calculate_warrior_threat()

    url_segments = urlparse(req.url)
    report_id = url_segments.path.split('/')[-1]
    fight_arg = url_segments.fragment.split('&')[0] if url_segments.fragment else None
    fight_num = fight_arg.split('=')[-1] if fight_arg and fight_arg.split('=')[-1].isdigit() else None
    
    redis = RedisClient()
    cached_data = await redis.get_report_results(report_id, req.player_name) or {}
    cached_data = {k: __recalculate_opts(v) for k, v in cached_data.items()}
    if cached_data:
        import copy
        if req.bosses:
            t = copy.deepcopy(cached_data)
            if all([b in t.keys() for b in req.bosses]):
                return {k: v for k, v in sorted({a: t[a] for a in req.bosses}.items(), key=lambda x: x[1].get('boss_id'))}
        if fight_num:
            t = copy.deepcopy(cached_data)
            f = {k: fight for k, fight in t.items() if str(fight.get('boss_id')) == fight_num}
            if f:
                return f
    
    wcl = WCLService()
    resp = await wcl.get_full_report(report_id)
    bosses = [f for f in resp.get('fights') if f.get('boss') != 0]
    if not bosses:
        raise HTTPException(status_code=400,
                            detail=f'No valid boss fights found in the linked log.')
    

    bosses = [boss for boss in bosses if boss.get('name') not in cached_data]
    if not bosses:
        return {k: v for k, v in sorted(cached_data.items(), key=lambda x: x[1].get('boss_id'))}

    if fight_num:
        bosses = [f for f in bosses if str(f.get('id', '')) == fight_num]
        if not bosses:
            raise HTTPException(status_code=400, detail=f'No boss activity found matching #fight={fight_num}')

    if req.bosses:
        bosses = [f for f in bosses if f.get('name') in req.bosses]
        if not bosses:
            raise HTTPException(status_code=400,
                                detail=f'No boss activity found matching {req.bosses}')

    player_info = [p for p in resp.get('friendlies') if p.get('name').lower() == req.player_name.lower()]
    if not player_info:
        raise HTTPException(status_code=400,
                            detail=f'Bad request: No player named {req.player_name} found in the linked log.')
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
    d = await get_player_activity(player_name, player_cls, realm, reqs, req.defiance_points, req.friendlies_in_combat, req.enemies_in_combat, req.t1_set) or {}
    return {k: v for k, v in sorted({**d, **cached_data}.items(), key=lambda x: x[1].get('boss_id'))}
 
async def get_player_activity(player_name, player_class, realm, reqs: List[BossActivityRequest], def_pts, friendlies, enemies, t1):
    if not reqs:
        return []
    wcl = WCLService()
    report_id = reqs[0].report_id if reqs[0] else None
    futures = [asyncio.gather(*[wcl.get_fight_details(req, event) for event in EVENTS]) for req in reqs]
    future_results = await asyncio.gather(*futures)
    results = []
    for fight in future_results:
        resp = {}
        for data in fight:
            resp.update({'time': data.get('totalTime') / 1000.0}) if data.get('totalTime') else {}
            info = await process_data_response(data.get('event'))(data)
            resp.update(dict(info), boss_name=data.get('boss_name'), boss_id=data.get('boss_id'))
        r = WarriorThreatCalculationRequest(**resp,
                                            player_name=player_name,
                                            player_class=player_class,
                                            realm=realm,
                                            defiance_points=def_pts,
                                            friendlies_in_combat=friendlies,
                                            enemies_in_combat=enemies,
                                            t1_bonus=t1,
                                            )

        tps = r.calculate_warrior_threat()
        results.append(tps)
    ret_json = {result.get('boss_name'): result for result in results}
    redis = RedisClient()
    await redis.save_results(report_id, player_name, ret_json)
    return ret_json


def process_data_response(request_type):
    return {
        'damage-done': process_damage_done,
        'casts': process_casts,
        'resources-gains': process_rage_gains,
        'healing': process_healing_done,
        'debuffs': process_debuffs
    }.get(request_type)


async def process_damage_done(data):
    damage_entries = data.get('entries')
    if not damage_entries:
        # Return 0 for damage or set the equivalent, dunno yet haven't gotten that far
        return WarriorDamageResponse(total_damage=0, execute_damage=0, sunder_count=0)
    total = []
    sunder_casts = 0
    execute_damage = 0
    for entry in damage_entries:
        if entry.get('name') == 'Sunder Armor':
            sunder_casts = entry.get('uses') - entry.get('missCount')
        elif entry.get('name') == 'Execute':
            execute_damage = entry.get('total')
        else:
            total.append(entry.get('total', 0))
    return WarriorDamageResponse(total_damage=sum(total) + execute_damage, execute_dmg=execute_damage, sunder_count=sunder_casts)


async def process_rage_gains(data):
    rage_gains = data.get('resources', [])
    rage_gain_events = [r.get('gains') for r in rage_gains]
    return {'rage_gains': sum(rage_gain_events)}


async def process_healing_done(data):
    healing_entries = data.get('entries')
    if not healing_entries:
        return {'hp_gains': 0}
    healing_events = [event.get('total') for event in healing_entries]
    return {'hp_gains': sum(healing_events)}


async def process_casts(data):
    cast_entries = data.get('entries')
    resp = WarriorCastResponse()

    if not cast_entries:
        return resp  # All 0 default vals

    abilities = {
        'Demoralizing Shout': 'demo_casts',
        'Battle Shout': 'bs_casts',
        'Shield Slam': 'shield_slam_count',
        'Heroic Strike': 'hs_count',
        'Revenge': 'revenge_count',
        'Thunder Clap': 'thunderclap_casts',
        'Bloodthirst': 'bt_count',
    }

    data = [entry for entry in cast_entries if entry.get('name') in abilities]
    resp = WarriorCastResponse()
    for entry in data:
        count = entry.get('hitCount', 0)
        name = entry.get('name')
        resp_attr = abilities.get(name)
        setattr(resp, resp_attr, count)
    return resp


async def process_debuffs(data):
    goa_procs = [d for d in data.get('auras') if d.get('name') == 'Gift of Arthas']
    if goa_procs:
        return {'goa_procs': goa_procs[0].get('totalUses')}
    return {'goa_procs': 0}



