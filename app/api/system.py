"""System and metadata routes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Dict

from fastapi import APIRouter

from ..config import get_weights_config, reload_weights
from ..models import ConfigResponse

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
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/version", summary="Version", description="Get API version information")
async def version() -> Dict[str, str]:
    """Get API version and build information."""
    weights_config = get_weights_config()
    return {
        "version": "1.0.0",
        "api_name": "CreditX API",
        "description": "Credit risk assessment and pricing system for insurance submissions and renewals",
        "build_date": "2025-01-03",
        "weights_version": weights_config.version,
    }


@router.post(
    "/admin/reload-weights",
    summary="Reload Weights",
    description="Reload weights.yaml from disk and return the active version.",
)
async def reload_weights_endpoint() -> Dict[str, str]:
    """Reload cached weights configuration."""
    weights_config = reload_weights()
    return {"status": "reloaded", "weights_version": weights_config.version}


@router.get(
    "/config/current",
    response_model=ConfigResponse,
    summary="Current Config",
    description="Return the current weights configuration including broker score curves and thresholds.",
)
async def current_config() -> ConfigResponse:
    config = get_weights_config()
    return {
        "version": config.version,
        "pricing_adjustments": config.pricing_adjustments.model_dump(),
        "pricing_bounds": config.pricing_bounds.model_dump(),
        "thresholds": config.thresholds.model_dump(),
        "broker_score_curves": {
            tier: curve.model_dump() for tier, curve in config.broker_score_curves.items()
        },
        "sector_coverage_limits": config.sector_coverage_limits,
    }
