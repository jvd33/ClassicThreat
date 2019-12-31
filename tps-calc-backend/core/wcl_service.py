import requests

PUB_KEY = '829648d907b8363b0694664963fd9319'
PRIV_KEY = 'd115f81a21ba849fbd375eee90d17a8b'


class WCLService:

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
            'api_key': PUB_KEY
        } if not params else {**params, 'api_key': PUB_KEY}

        resp= requests.request(method,
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

    async def get_fight_details(self, report_id, view, target_player_id):
        url = self.base_url + f'report/events/{view}/{report_id}'
        return url
