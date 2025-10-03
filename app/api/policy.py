"""Policy validation endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from ..config import get_weights_config
from ..models import PolicyCheckRequest, PolicyCheckResponse

router = APIRouter()


@router.post(
    "/check",
    response_model=PolicyCheckResponse,
    summary="Policy Coverage Check",
    description=(
        "Validate requested coverage percentage against sector thresholds. "
        "Returns failure if the requested percentage exceeds the configured maximum."
    ),
)
async def policy_check(payload: PolicyCheckRequest) -> PolicyCheckResponse:
    config = get_weights_config()
    limits = config.sector_coverage_limits
    sector_limit = limits.get(payload.sector, limits.get("default", 1.0))

    if payload.requested_cov_pct > sector_limit:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Requested coverage {payload.requested_cov_pct:.2f} exceeds limit {sector_limit:.2f} "
                f"for sector {payload.sector}."
            ),
        )

    return PolicyCheckResponse(
        allowed=True,
        sector=payload.sector,
        requested_cov_pct=payload.requested_cov_pct,
        max_allowed_cov_pct=sector_limit,
    )
