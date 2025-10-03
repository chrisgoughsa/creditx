"""System and metadata routes."""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Root", description="API root endpoint")
async def root() -> Dict[str, str]:
    """API root endpoint."""
    return {"message": "CreditX API", "version": "1.0.0"}


@router.get("/health", summary="Health Check", description="Health check endpoint for monitoring")
async def health() -> Dict[str, str]:
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "message": "CreditX API is running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


@router.get("/version", summary="Version", description="Get API version information")
async def version() -> Dict[str, str]:
    """Get API version and build information."""
    return {
        "version": "1.0.0",
        "api_name": "CreditX API",
        "description": "Credit risk assessment and pricing system for insurance submissions and renewals",
        "build_date": "2025-01-03",
        "weights_version": "1.0.0",
    }
