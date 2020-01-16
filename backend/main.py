import asyncio
import uvicorn

from fastapi import FastAPI, Header, HTTPException
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv

from core import routes

load_dotenv(find_dotenv())
origins = [
    "*",
]


app = FastAPI(
            redoc_url="/api/v1/docs", 
            docs_url=None,
            title="ClassicThreat API",
            description="Provides a mechanism to parse Warcraft Logs data for information more valuable for tanks.",
            version="0.5.0",
            openapi_url="/api/v1/openapi.json"
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.api_router, prefix='/api/v1')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)