"""FastAPI application for credit risk assessment and pricing system."""

from __future__ import annotations

from fastapi import FastAPI

from .api import api_router


app = FastAPI(
    title="CreditX API",
    description="Credit risk assessment and pricing system for insurance submissions and renewals",
    version="1.0.0",
    contact={"name": "CreditX"},
)


app.include_router(api_router)
