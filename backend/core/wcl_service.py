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
                                   translate=True,
                                   **kwargs):

        __request = {'GET': self.session.get, 'POST': self.session.post}.get(method, None)
        if not __request:
            raise HTTPException(status_code=400, detail="Bad request")
        headers = {'content-type': 'application/json', 'accept-encoding': 'gzip'}
        api_key = random.choice(self.wcl_keys)
        query = {
            'api_key': api_key
        } if not params else {**params, 'api_key': api_key}
        if translate:
            query.update({'translate': 'true'})

        logger.error(f'{method}: {url}, {params}, {data}')
        async with await __request(url, params=query, json=data or '{}', headers=headers) as resp:
            return await resp.content.read()


    async def get_full_report(self, report_id):
        url = self.base_url + f'report/fights/{report_id}'
        resp = await self._send_scoped_request('GET', url)
        data = ujson.loads(resp)
        if not data.get('fights'):
            resp = await self._send_scoped_request('GET', url, translate=False)
        return ujson.loads(resp)

    async def get_fight_details(self, req: BossActivityRequest):

        url = self.base_url + f'report/events/summary/{req.report_id}'
        params = {
            'start': req.start_time,
            'end': req.end_time,
            'sourceid': req.player_id
        }
            
        resp = await self._send_scoped_request('GET', url, params=params)
        if not resp:
            resp = await self._send_scoped_request('GET', url, params=params, translate=False) or {}
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
        if not resp:
            resp = await self._send_scoped_request('GET', url, params=params, translate=False)
        ret = ujson.loads(resp)
        ret.update({'event': 'stance', 'boss_name': req.boss_name, 'boss_id': req.encounter, 'start_time': req.start_time})
        return ret


    async def get_dps_details(self, req: BossActivityRequest):
        url = self.base_url + f'report/tables/damage-done/{req.report_id}'
        casts = self.base_url + f'report/tables/casts/{req.report_id}'
        params = {
            'start': req.start_time,
            'end': req.end_time,
        }

        damage_resp = await self._send_scoped_request('GET', url, params=params)
        casts_resp = await self._send_scoped_request('GET', casts, params=params)

        try:
            damage = ujson.loads(damage_resp)
            casts = ujson.loads(casts_resp)
        except Exception as e:
            damage_resp = await self._send_scoped_request('GET', url, params=params, translate=False)
            casts_resp = await self._send_scoped_request('GET', casts, params=params, translate=False)
            damage = ujson.loads(damage_resp)
            casts = ujson.loads(casts_resp)

        data = []
        from .utils import flatten
        for player in damage.get('entries'):
            if player.get('type').casefold() in ['warrior', 'druid']:
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
