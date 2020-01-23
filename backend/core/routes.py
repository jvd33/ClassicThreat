import ujson
import aiohttp
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from aiohttp import ClientResponseError
from starlette.responses import JSONResponse

from .models.common import WCLDataRequest
from .models.warrior import WarriorThreatResult
from .models.druid import DruidThreatResult
from .tasks.warrior import get_log_data as warr_get_log_data
from .tasks.druid import get_log_data as druid_get_log_data
from .constants import WarriorThreatValues, Threat, DruidThreatValues
from docs.examples import CALC_RESP_EXAMPLE, THREAT_RESP_EXAMPLE, HEARTBEAT, CALC_RESP_DRUID_EXAMPLE
from .cache import RedisClient

api_router = APIRouter()

async def _refresh_cache(db):
    r = RedisClient()
    await r.refresh_rank_data(db=db)

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


@api_router.post('/calculate_warrior', 
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
async def calculate_warrior(req: WCLDataRequest, background_tasks: BackgroundTasks, session=Depends(get_http_session), ):
    try:
        async with session:
            results = await warr_get_log_data(req, session=session)
            background_tasks.add_task(_refresh_cache, 2)
            return JSONResponse(content=results, status_code=200)
    except ClientResponseError as cexc:
        return JSONResponse(content={'detail': f'Error from Warcraft Logs: {cexc.message}', 'code': cexc.status}, status_code=cexc.status)
    except HTTPException as hexc:
        raise hexc

@api_router.post('/calculate_druid', 
                tags=['v1'], 
                dependencies=[Depends(get_http_session)], 
                response_model=DruidThreatResult,
                responses={
                            404: {
                                "description": "The report was not found, no player with the name was found in the report, or there were no valid boss fights found."
                            },
                            200: {
                                "description": "Threat calculation succeeded",
                                "content": {
                                    "application/json": {
                                        "example": CALC_RESP_DRUID_EXAMPLE
                                    }
                                },
                            },
                            400: {
                                "description": "Bad response to WCL"
                                },
                            },
                )
async def calculate_druid(req: WCLDataRequest, background_tasks: BackgroundTasks, session=Depends(get_http_session), ):
    try:
        async with session:
            results = await druid_get_log_data(req, session=session)
            background_tasks.add_task(_refresh_cache, 3)
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
async def get_threat_values(player_class):
    if player_class == 'Warrior':
        vals = WarriorThreatValues.items()
    elif player_class == 'Druid':
        vals = DruidThreatValues.items()
    else:
        return JSONResponse(content={'detail': 'Invalid Class'}, status_code=400)
    ret = [{'name': val.get('name'), **val.get('val')} for val in vals]
    ret.append({'name': 'Damage', 'threat_type': 'Flat', 'val': 1})
    return JSONResponse(content=ret, status_code=200)


@api_router.get('/rankings', 
                tags=['v1'], 
                responses={
                            200: {
                                "description": "Successful response",
                                "content": {
                                    "application/json": {
                                        "example": {}
                                    }
                                },
                            },
                        },
                )
async def get_boss_rankings(boss, class):
    db = {
        'Warrior': 2,
        'Druid': 3
    }.get(player_class, None)
    if not db:
        return JSONResponse(content={'detail': 'Invalid Player Class'}, status_code=400)
    r = RedisClient()
    ranks = await r.get_encounter_rankings(boss_name, db=db)
    return JSONResponse(content=ranks, status_code=200)