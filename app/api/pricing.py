"""Pricing API routes."""

from __future__ import annotations

from fastapi import APIRouter

from ..features import prepare_submissions_features
from ..models import BatchSubmissions, PricingResults
from ..service import pricing_suggestions

router = APIRouter()


@router.post(
    "/suggest",
    response_model=PricingResults,
    summary="Pricing Suggestions",
    description=(
        "Generate pricing suggestions for credit insurance submissions based on sector rates and risk adjustments. "
        "Returns suggested rates in basis points, risk bands, and detailed adjustments applied to the base sector rate."
    ),
)
async def pricing_suggest(batch: BatchSubmissions) -> PricingResults:
    """Generate pricing suggestions for submissions."""
    submissions_data = [submission.model_dump() for submission in batch.submissions]
    submissions_df = prepare_submissions_features(submissions_data)
    result = pricing_suggestions(submissions_df)
    return PricingResults(**result)
