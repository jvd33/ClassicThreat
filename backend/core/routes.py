from fastapi import APIRouter

from .models import WCLDataRequest
from .tasks import get_log_data

router = APIRouter()
api_router = APIRouter()


@router.get('/')
async def index():
    return {'status': 'OK'}


@api_router.post('/calculate', tags=['api'])
async def calculate(req: WCLDataRequest):
    pass