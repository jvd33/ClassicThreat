import ujson

from fastapi import APIRouter, HTTPException
from requests.exceptions import HTTPError

from .models import WCLDataRequest
from .tasks import get_log_data
from .constants import ThreatValues

api_router = APIRouter()


@api_router.get('/status', tags=['api'])
async def status():
    return {'status': 'OK'}


@api_router.post('/calculate', tags=['api'])
async def calculate(req: WCLDataRequest):
    try:
        return await get_log_data(req)
    except HTTPError as exc:
        raise exc
        raise HTTPException(status_code=exc.response.status_code, detail="Bad response from WCL")
    except HTTPException as exc:
        raise exc


@api_router.get('/threat_values', tags=['api'])
async def get_threat_values():
    vals = ThreatValues.items()
    ret = [{'name': val.get('name'), **val.get('val')} for val in vals]
    ret.append({'name': 'Damage', 'threat_type': 'Flat', 'val': 1})
    return ujson.dumps(ret)
