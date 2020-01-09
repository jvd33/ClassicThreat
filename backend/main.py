import asyncio

from fastapi import FastAPI, Header, HTTPException
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core import routes

load_dotenv()
origins = [
    "*",
]


app = FastAPI(
            redoc_url="/api/v1/docs", 
            docs_url=None,
            title="ClassicThreat API",
            description="Provides a mechanism to parse Warcraft Logs data for information more valuable for tanks.",
            version="0.5.0"
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.api_router, prefix='/api/v1', tags=['v1'])
