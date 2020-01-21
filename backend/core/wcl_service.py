import os
import ujson
import logging
import random

from fastapi import HTTPException

from .models import BossActivityRequest, Spell

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

    async def get_fight_details(self, req: BossActivityRequest, event):
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