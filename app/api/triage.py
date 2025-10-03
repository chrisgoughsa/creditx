"""Underwriting triage API routes."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, File, UploadFile

from ..features import prepare_submissions_features
from ..models import BatchSubmissions, TriageScore
from ..service import triage_scores
from .common import (
    SUBMISSION_COLUMNS,
    convert_submission_row,
    parse_csv_upload,
)

router = APIRouter()


@router.post(
    "/underwriting",
    response_model=List[TriageScore],
    summary="Underwriting Triage",
    description=(
        "Calculate triage scores for credit insurance submissions to prioritize underwriting review. "
        "Scores are based on exposure limits, debtor days, financial documentation, trading history, "
        "broker quality, and risk factors like outstanding judgements."
    ),
)
async def triage_underwriting(batch: BatchSubmissions) -> List[TriageScore]:
    """Triage submissions for underwriting priority."""
    submissions_data = [submission.model_dump() for submission in batch.submissions]
    submissions_df = prepare_submissions_features(submissions_data)
    result = triage_scores(submissions_df)
    return [TriageScore(**score) for score in result["scores"]]


@router.post(
    "/underwriting/csv",
    response_model=List[TriageScore],
    summary="Underwriting Triage (CSV Upload)",
    description=(
        "Upload CSV file for underwriting triage. CSV must contain columns: submission_id, broker, sector, "
        "exposure_limit, debtor_days, financials_attached, years_trading, broker_hit_rate, requested_cov_pct, "
        "has_judgements. Boolean fields accept: true/false, 1/0, yes/no, y/n."
    ),
)
async def triage_underwriting_csv(file: UploadFile = File(...)) -> List[TriageScore]:
    """Upload CSV for triage scoring."""
    submissions_data = await parse_csv_upload(
        file,
        required_columns=SUBMISSION_COLUMNS,
        file_type="submissions",
        row_converter=convert_submission_row,
    )
    submissions_df = prepare_submissions_features(submissions_data)
    result = triage_scores(submissions_df)
    return [TriageScore(**score) for score in result["scores"]]
