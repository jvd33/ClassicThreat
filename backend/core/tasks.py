import asyncio

from urllib.parse import urlparse
from typing import List

from .models import WCLDataRequest, BossActivityRequest, WarriorCastResponse, \
    WarriorDamageResponse, WarriorThreatCalculationRequest
from .wcl_service import WCLService

EVENTS = ['damage-done', 'casts', 'resources-gains', 'healing', 'debuffs']


async def get_log_data(req: WCLDataRequest):
    url_segments = urlparse(req.url)
    report_id = url_segments.path.split('/')[-1]
    fight_arg = url_segments.fragment.split('&')[0] if url_segments.fragment else None
    fight_num = fight_arg.split('=')[-1] if fight_arg else None

    wcl = WCLService()
    resp = await wcl.get_full_report(report_id)
    all_bosses = [f for f in resp.get('fights') if f.get('boss') != 0]
    bosses = all_bosses

    if fight_num:
        bosses = [f for f in all_bosses if str(f.get('id', '')) == fight_num]
    if req.bosses:
        bosses = [f for f in all_bosses if f.get('name') in req.bosses]

    player_info = [p for p in resp.get('friendlies') if p.get('name').lower() == req.player_name.lower()]
    if not player_info:
        raise KeyError
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
        report_id=report_id,
    ) for boss in bosses]

    return await get_player_activity(player_name, player_cls, realm, reqs)


async def get_player_activity(player_name, player_class, realm, reqs: List[BossActivityRequest]):
    wcl = WCLService()
    futures = [asyncio.gather(*[wcl.get_fight_details(req, event) for event in EVENTS]) for req in reqs]
    future_results = await asyncio.gather(*futures)
    results = []
    for fight in future_results:
        resp = {}
        for data in fight:
            resp.update({'time': data.get('totalTime') / 1000.0}) if data.get('totalTime') else {}
            info = await process_data_response(data.get('event'))(data)
            resp.update(dict(info))
        r = WarriorThreatCalculationRequest(**resp,
                                            player_name=player_name,
                                            player_class=player_class,
                                            realm=realm)
        tps = r.calculate_warrior_threat()
        results.append(tps)
    return results


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
    print(sunder_casts)
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



