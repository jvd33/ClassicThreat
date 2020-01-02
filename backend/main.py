import asyncio

from fastapi import FastAPI, Header, HTTPException
from starlette.middleware.cors import CORSMiddleware

from core import routes

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://localhost:8080",
    "localhost:8080"
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.api_router, prefix='/v1/api', tags=['api'])
