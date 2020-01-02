from fastapi import APIRouter, HTTPException
from requests.exceptions import HTTPError

from .models import WCLDataRequest
from .tasks import get_log_data

api_router = APIRouter()


@api_router.get('/status', tags=['api'])
async def index():
    return {'status': 'OK'}


@api_router.post('/calculate', tags=['api'])
async def calculate(req: WCLDataRequest):
    try:
        resp = await get_log_data(req)
        return resp
    except HTTPError as exc:
        raise HTTPException(status_code=exc.response.status_code)
    except HTTPException as exc:
        raise exc
