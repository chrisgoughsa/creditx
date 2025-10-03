"""FastAPI application for credit risk assessment and pricing system."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import api_router


app = FastAPI(
    title="CreditX API",
    description="Credit risk assessment and pricing system for insurance submissions and renewals",
    version="1.0.0",
    contact={"name": "CreditX"},
)


ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)
