import asyncio

from fastapi import FastAPI, Header, HTTPException
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core import routes

load_dotenv()
origins = [
    "http://localhost",
    "https://localhost",
    "http://localhost:8080",
    "https://localhost:8080",
    "http://classicthreat-ui:8080",
    "http://classicthreat-ui",
    "http://classicthreat.com",
    "https://classicthreat.com",
    "http://classicthreat-api",
    "https://classicthreat-api",
    "http://frontend.classicthreat-service",
    "http://frontend.classicthreat-service",

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
