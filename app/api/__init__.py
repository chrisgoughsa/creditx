"""API router aggregation for CreditX."""

from fastapi import APIRouter

from . import policy, pricing, renewals, system, triage

api_router = APIRouter()
api_router.include_router(triage.router, prefix="/triage", tags=["Underwriting Triage"])
api_router.include_router(renewals.router, prefix="/renewals", tags=["Renewal Priority"])
api_router.include_router(pricing.router, prefix="/pricing", tags=["Pricing"])
api_router.include_router(policy.router, prefix="/policy", tags=["Policy"])
api_router.include_router(system.router, tags=["System"])

__all__ = ["api_router"]
