import requests
import os
from dotenv import load_dotenv
from .models import BossActivityRequest


class WCLService:
    load_dotenv()
    PUB_KEY = os.getenv('WCL_PUB_KEY')

    def __init__(self):
        self.base_url = 'https://www.warcraftlogs.com/v1/'

    async def _send_scoped_request(self,
                                   method: str,
                                   url: str,
                                   data: any = None,
                                   params: any = None,
                                   stream: bool = False,
                                   **kwargs):

        headers = {'content-type': 'application/json'}
        if stream:
            headers.update({'accept-encoding': 'gzip'})

        params = {
            'api_key': self.PUB_KEY
        } if not params else {**params, 'api_key': self.PUB_KEY}
        print(f'{method}: {url}')
        resp = requests.request(method,
                                url,
                                params=params,
                                data=data,
                                headers=headers,
                                stream=stream,
                                **kwargs)
        return resp

    async def get_full_report(self, report_id):
        url = self.base_url + f'report/fights/{report_id}'
        resp = await self._send_scoped_request('GET', url, stream=True)
        resp.raise_for_status()
        return resp.json()

    async def get_fight_details(self, req: BossActivityRequest, event):
        url = self.base_url + f'report/tables/{event}/{req.report_id}'
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
        ret = resp.json()
        ret.update({'event': event, 'boss_name': req.boss_name})
        return ret
