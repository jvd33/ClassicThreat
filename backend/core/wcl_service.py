import os
import ujson
import logging
import random

from fastapi import HTTPException

from .models.common import BossActivityRequest 
from .constants import Spell

logger = logging.getLogger()

class WCLService:

    def __init__(self, session):
        self.base_url = 'https://www.warcraftlogs.com/v1/'
        self.session = session
        self.wcl_keys = os.getenv('WCL_PUB_KEYS').split(',')


    async def _send_scoped_request(self,
                                   method: str,
                                   url: str,
                                   data: any = None,
                                   params: any = None,
                                   **kwargs):

        __request = {'GET': self.session.get, 'POST': self.session.post}.get(method, None)
        if not __request:
            raise HTTPException(status_code=400, detail="Bad request")
        headers = {'content-type': 'application/json', 'accept-encoding': 'gzip'}
        api_key = random.choice(self.wcl_keys)
        query = {
            'translate': 'true',   # Turns out WCL breaks if you pass it boolean True LOL
            'api_key': api_key
        } if not params else {**params, 'translate': 'true', 'api_key': api_key}

        logger.error(f'{method}: {url}, {params}, {data}')
        async with await __request(url, params=query, json=data or '{}', headers=headers) as resp:
            return await resp.content.read()


    async def get_full_report(self, report_id):
        url = self.base_url + f'report/fights/{report_id}'
        resp = await self._send_scoped_request('GET', url)
        return ujson.loads(resp)

    async def get_fight_details(self, req: BossActivityRequest):

        url = self.base_url + f'report/events/summary/{req.report_id}'
        params = {
            'start': req.start_time,
            'end': req.end_time,
            'sourceid': req.player_id
        }

            
        resp = await self._send_scoped_request('GET', url, params=params)
        ret = ujson.loads(resp)
        ret.update({
            'boss_name': req.boss_name, 
            'boss_id': req.encounter, 
            'total_time': req.end_time - req.start_time,
            'start_time': req.start_time,
            'end_time': req.end_time,
            'player_id': req.player_id
        })
        return ret

    async def get_stance_state(self, req: BossActivityRequest):
        url = self.base_url + f'report/events/buffs/{req.report_id}'
        params = {
            'start': req.start_time,
            'end': req.end_time,
            'sourceid': req.player_id
        }
            
        resp = await self._send_scoped_request('GET', url, params=params)
        ret = ujson.loads(resp)
        ret.update({'event': 'stance', 'boss_name': req.boss_name, 'boss_id': req.encounter, 'start_time': req.start_time})
        return ret


    async def get_dps_details(self, req: BossActivityRequest):
        url = self.base_url + f'report/tables/damage-done/{req.report_id}'
        casts = self.base_url + f'report/tables/casts/{req.report_id}'
        params = {
            'start': req.start_time,
            'end': req.end_time,
            'sourceclass': 'warrior'
        }

        damage_resp = await self._send_scoped_request('GET', url, params=params)
        casts_resp = await self._send_scoped_request('GET', casts, params=params)
        damage, casts = ujson.loads(damage_resp), ujson.loads(casts_resp)
        data = []
        from .utils import flatten
        for player in damage.get('entries'):
            data.append({
                'player_name': player.get('name'),
                'damage': player.get('abilities'),
                'boss_name': req.boss_name,
                'total': player.get('total'),
                'casts': flatten([e.get('abilities') for e in casts.get('entries') if e.get('name') == player.get('name')]),
                'gear': player.get('gear')
            })
        ret = []
        for r in data:
            dmg = r.get('damage')
            casts = r.get('casts')
            execute_dmg = [e.get('total') for e in dmg if e.get('name') == 'Execute']
            hs_casts = [e.get('total') for e in casts if e.get('name') == 'Heroic Strike']
            d = {
                'player_name': r.get('player_name'),
                'player_id': r.get('id'),
                'hs_casts':  hs_casts[0] if hs_casts else 0,
                'execute_dmg': execute_dmg[0] if execute_dmg else 0,
                'total_dmg': r.get('total'),
                'boss_name': r.get('boss_name'),
                'gear': r.get('gear')
            }
            ret.append(d)
        return ret

    async def get_fight_details_depr(self, req: BossActivityRequest, event):
        ep = 'events'
        if event in ['resources-gains', 'healing']:
            ep = 'tables'
        url = self.base_url + f'report/{ep}/{event}/{req.report_id}'
        params = {
            'start': req.start_time,
            'end': req.end_time,
            'sourceid': req.player_id
        }
        if event == 'resources-gains':
            #  I really like this one. WCL counts specific resource types as "abilities" with arbitrary IDs
            #  No idea where these id came from, but rage is 101. lol 'abilityid' param mega jank
            params.update({
                'by': 'ability',
                'abilityid': 101
            })
        if event == 'debuffs':
            del params['sourceid']
            params.update({
                'hostility': 1,
                'targetid': req.player_id
            })
            
        resp = await self._send_scoped_request('GET', url, params=params)
        ret = ujson.loads(resp)
        ret.update({'event': event, 'boss_name': req.boss_name, 'boss_id': req.encounter})
        return ret
