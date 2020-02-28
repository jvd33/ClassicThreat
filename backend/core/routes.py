import ujson
import aiohttp
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import List
from aiohttp import ClientResponseError
from starlette.responses import JSONResponse

from .models.common import WCLDataRequest, FightLog
from .models.warrior import WarriorThreatResult
from .models.druid import DruidThreatResult
from .models.paladin import PaladinThreatResult
from .tasks import get_log_data
from .constants import WarriorThreatValues, Threat, DruidThreatValues, PaladinThreatValues
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
            results, _ = await get_log_data(req, session=session, player_class='warrior')
            background_tasks.add_task(_refresh_cache, 2)
            return JSONResponse(content=results, status_code=200)
    except ClientResponseError as cexc:
        return JSONResponse(content={'detail': f'Error from Warcraft Logs: {cexc.message}', 'code': cexc.status}, status_code=cexc.status)
    except HTTPException as hexc:
        raise hexc
    finally:
        await session.close()


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
            results, _ = await get_log_data(req, session=session, player_class='druid')
            background_tasks.add_task(_refresh_cache, 3)
            return JSONResponse(content=results, status_code=200)
    except ClientResponseError as cexc:
        return JSONResponse(content={'detail': f'Error from Warcraft Logs: {cexc.message}', 'code': cexc.status}, status_code=cexc.status)
    except HTTPException as hexc:
        raise hexc
    finally:
        await session.close()


@api_router.post('/calculate_paladin', 
                tags=['v1'], 
                dependencies=[Depends(get_http_session)], 
                response_model=PaladinThreatResult,
                responses={
                            404: {
                                "description": "The report was not found, no player with the name was found in the report, or there were no valid boss fights found."
                            },
                            200: {
                                "description": "Threat calculation succeeded",
                                "content": {
                                    "application/json": {
                                        "example": {}
                                    }
                                },
                            },
                            400: {
                                "description": "Bad response to WCL"
                                },
                            },
                )
async def calculate_paladin(req: WCLDataRequest, background_tasks: BackgroundTasks, session=Depends(get_http_session), ):
    try:
        async with session:
            results, _ = await get_log_data(req, session=session, player_class='paladin')
            background_tasks.add_task(_refresh_cache, 6)
            return JSONResponse(content=results, status_code=200)
    except ClientResponseError as cexc:
        return JSONResponse(content={'detail': f'Error from Warcraft Logs: {cexc.message}', 'code': cexc.status}, status_code=cexc.status)
    except HTTPException as hexc:
        raise hexc
    finally:
        await session.close()

@api_router.get('/events/{report_id}/{player_name}',
                tags=['v1'],
                dependencies=[Depends(get_http_session)], 

                )
async def get_event_timeline(report_id, player_name, player_class, session=Depends(get_http_session), boss: List[str]=Query(None)):
    try:
        events = None
        r = RedisClient()
        try:
            events = await r.get_events(report_id, player_name, bosses=boss)
        except ConnectionRefusedError:
            pass
        if not events:
            async with session:
                req = WCLDataRequest(
                    url=f'https://classic.warcraftlogs.com/reports/{report_id}',
                    player_name=player_name,
                    talent_pts=5,
                    bosses=boss or [],
                )
                _, events = await get_log_data(req, session=session, player_class=player_class.casefold())

        return JSONResponse(content={k: e.dict() for k, e in events.items()}, status_code=200)

    except ClientResponseError as cexc:
        return JSONResponse(content={'detail': f'Error from Warcraft Logs: {cexc.message}', 'code': cexc.status}, status_code=cexc.status)
    except HTTPException as hexc:
        raise hexc
    finally:
        await session.close()

    
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
    elif player_class == 'Paladin':
        vals = PaladinThreatValues.items()
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
async def get_boss_rankings(boss, player_class):
    db = {
        'Warrior': 2,
        'Druid': 3,
        'Paladin': 6
    }.get(player_class, None)
    if not db:
        return JSONResponse(content={'detail': 'Invalid Player Class'}, status_code=400)
    r = RedisClient()
    ranks = await r.get_encounter_rankings(boss, db=db)
    ranks = [{**v[1], **{'rank': i + 1}} for i, v in enumerate(ranks.items())]
    return JSONResponse(content=ranks[:501], status_code=200)