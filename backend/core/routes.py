import ujson
import aiohttp
from fastapi import APIRouter, HTTPException, Depends
from aiohttp import ClientResponseError
from starlette.responses import JSONResponse

from .models import WCLDataRequest, WarriorThreatResult
from .tasks import get_log_data
from .constants import WarriorThreatValues, Threat
from docs.examples import CALC_RESP_EXAMPLE, THREAT_RESP_EXAMPLE, HEARTBEAT

api_router = APIRouter()

async def get_http_session():
    return aiohttp.ClientSession(json_serialize=ujson.dumps, raise_for_status=True)

@api_router.get('/status', 
                tags=['v1'],
                responses={
                    200: {
                        "description": "Used to check API availability status",
                        "content": {
                            "application/json": {
                                "example": HEARTBEAT
                                }
                            }
                        },
                    }
                )
async def status():
    return JSONResponse(content={'status': 'OK'}, status_code=200)


@api_router.post('/calculate', 
                tags=['v1'], 
                dependencies=[Depends(get_http_session)], 
                response_model=WarriorThreatResult,
                responses={
                            404: {
                                "description": "The report was not found, no player with the name was found in the report, or there were no valid boss fights found."
                            },
                            200: {
                                "description": "Threat calculation succeeded",
                                "content": {
                                    "application/json": {
                                        "example": CALC_RESP_EXAMPLE
                                    }
                                },
                            },
                            400: {
                                "description": "Bad response to WCL"
                                },
                            },
                )
async def calculate(req: WCLDataRequest, session=Depends(get_http_session)):
    try:
        async with session:
            results = await get_log_data(req, session=session)
            return JSONResponse(content=results, status_code=200)
    except ClientResponseError as cexc:
        return JSONResponse(content={'detail': f'Error from Warcraft Logs: {cexc.message}', 'code': cexc.status}, status_code=cexc.status)
    except HTTPException as hexc:
        raise hexc


@api_router.get('/threat_values', 
                tags=['v1'], 
                response_model=Threat,
                responses={
                            200: {
                                "description": "Threat calculation succeeded",
                                "content": {
                                    "application/json": {
                                        "example": THREAT_RESP_EXAMPLE
                                    }
                                },
                            },
                        },
                )
async def get_threat_values():
    vals = ThreatValues.items()
    ret = [{'name': val.get('name'), **val.get('val')} for val in vals]
    ret.append({'name': 'Damage', 'threat_type': 'Flat', 'val': 1})
    return JSONResponse(content=ret, status_code=200)
