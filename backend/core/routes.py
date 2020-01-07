import ujson
import aiohttp
from fastapi import APIRouter, HTTPException, Depends
from aiohttp import ClientResponseError

from .models import WCLDataRequest
from .tasks import get_log_data
from .constants import ThreatValues

api_router = APIRouter()

async def get_http_session():
    return aiohttp.ClientSession(json_serialize=ujson.dumps)

@api_router.get('/status', tags=['api'])
async def status():
    return {'status': 'OK'}


@api_router.post('/calculate', tags=['api'], dependencies=[Depends(get_http_session)])
async def calculate(req: WCLDataRequest, session=Depends(get_http_session)):
    try:
        async with session:
            return await get_log_data(req, session=session)
    except ClientResponseError as exc:
        raise HTTPException(status_code=exc.status, detail=exc.message)
    except HTTPException as exc:
        raise exc


@api_router.get('/threat_values', tags=['api'])
async def get_threat_values():
    vals = ThreatValues.items()
    ret = [{'name': val.get('name'), **val.get('val')} for val in vals]
    ret.append({'name': 'Damage', 'threat_type': 'Flat', 'val': 1})
    return ujson.dumps(ret)
