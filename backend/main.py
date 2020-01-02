import asyncio

from fastapi import FastAPI, Header, HTTPException

from core import routes


app = FastAPI()

app.include_router(routes.router)
app.include_router(routes.api_router, prefix='/v1/api', tags=['api'])
