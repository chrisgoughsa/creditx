"""Renewal priority API routes."""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from ..features import prepare_policies_features
from ..models import BatchPolicies, RenewalResults
from ..service import renewals_priority
from .common import (
    POLICY_COLUMNS,
    convert_policy_row,
    parse_csv_upload,
)

router = APIRouter()


@router.post(
    "/priority",
    response_model=RenewalResults,
    summary="Renewal Priority",
    description=(
        "Calculate priority scores for policy renewals based on expiry dates, utilization rates, "
        "claims history, and client requests. Higher scores indicate more urgent renewal processing needs."
    ),
)
async def renewals_priority_endpoint(batch: BatchPolicies) -> RenewalResults:
    """Calculate renewal priority for policies."""
    policies_data = [policy.model_dump() for policy in batch.policies]
    policies_df = prepare_policies_features(policies_data)
    result = renewals_priority(policies_df)
    return RenewalResults(**result)


@router.post(
    "/priority/csv",
    response_model=RenewalResults,
    summary="Renewal Priority (CSV Upload)",
    description=(
        "Upload CSV file for renewal priority scoring. CSV must contain columns: policy_id, sector, current_premium, "
        "limit, utilization_pct, claims_last_24m_cnt, claims_ratio_24m, days_to_expiry, requested_change_pct, broker."
    ),
)
async def renewals_priority_csv(file: UploadFile = File(...)) -> RenewalResults:
    """Upload CSV for renewal priority scoring."""
    policies_data = await parse_csv_upload(
        file,
        required_columns=POLICY_COLUMNS,
        file_type="policies",
        row_converter=convert_policy_row,
    )
    policies_df = prepare_policies_features(policies_data)
    result = renewals_priority(policies_df)
    return RenewalResults(**result)
