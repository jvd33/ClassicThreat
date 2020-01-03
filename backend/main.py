import asyncio

from fastapi import FastAPI, Header, HTTPException
from starlette.middleware.cors import CORSMiddleware

from core import routes

origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8080",
    "https://localhost:8080",
    "http://frontend:8080",
    "https://frontend:8080",
    "http://classicthreat.com",
    "https://classicthreat.com",
    "http://classicthreat.com:8080",
    "https://classicthreat.com:8080"
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
