"""FastAPI application for credit risk assessment and pricing system."""

import csv
import io
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

from .models import (
    BatchSubmissions, 
    BatchPolicies, 
    TriageScore, 
    PriceSuggestion
)
from .features import prepare_submissions_features, prepare_policies_features
from .service import triage_scores, renewals_priority, pricing_suggestions

# Initialize FastAPI app
app = FastAPI(
    title="CreditX API",
    description="Credit risk assessment and pricing system for insurance submissions and renewals",
    version="1.0.0"
)

# Required columns for CSV validation
SUBMISSION_COLUMNS = {
    "submission_id", "broker", "sector", "exposure_limit", "debtor_days",
    "financials_attached", "years_trading", "broker_hit_rate", 
    "requested_cov_pct", "has_judgements"
}

POLICY_COLUMNS = {
    "policy_id", "sector", "current_premium", "limit", "utilization_pct",
    "claims_last_24m_cnt", "claims_ratio_24m", "days_to_expiry",
    "requested_change_pct", "broker"
}


def validate_csv_columns(columns: List[str], required_columns: set, file_type: str) -> None:
    """Validate that CSV has all required columns."""
    missing_columns = required_columns - set(columns)
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns in {file_type} CSV: {', '.join(sorted(missing_columns))}. "
                   f"Required columns: {', '.join(sorted(required_columns))}"
        )


def parse_csv_to_dicts(csv_content: str) -> List[Dict[str, Any]]:
    """Parse CSV content to list of dictionaries."""
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    return list(csv_reader)


def convert_submission_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Convert CSV row to submission dictionary with proper types."""
    # Check for missing required fields
    for field in SUBMISSION_COLUMNS:
        if field not in row or row[field] is None or row[field].strip() == "":
            raise KeyError(f"Missing required field: {field}")
    
    return {
        "submission_id": row["submission_id"],
        "broker": row["broker"],
        "sector": row["sector"],
        "exposure_limit": float(row["exposure_limit"]),
        "debtor_days": float(row["debtor_days"]),
        "financials_attached": row["financials_attached"].lower() in ("true", "1", "yes", "y"),
        "years_trading": float(row["years_trading"]),
        "broker_hit_rate": float(row["broker_hit_rate"]),
        "requested_cov_pct": float(row["requested_cov_pct"]),
        "has_judgements": row["has_judgements"].lower() in ("true", "1", "yes", "y")
    }


def convert_policy_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Convert CSV row to policy dictionary with proper types."""
    # Check for missing required fields
    for field in POLICY_COLUMNS:
        if field not in row or row[field] is None or row[field].strip() == "":
            raise KeyError(f"Missing required field: {field}")
    
    return {
        "policy_id": row["policy_id"],
        "sector": row["sector"],
        "current_premium": float(row["current_premium"]),
        "limit": float(row["limit"]),
        "utilization_pct": float(row["utilization_pct"]),
        "claims_last_24m_cnt": int(row["claims_last_24m_cnt"]),
        "claims_ratio_24m": float(row["claims_ratio_24m"]),
        "days_to_expiry": float(row["days_to_expiry"]),
        "requested_change_pct": float(row["requested_change_pct"]),
        "broker": row["broker"]
    }


@app.post(
    "/triage/underwriting",
    response_model=List[TriageScore],
    summary="Underwriting Triage",
    description="Calculate triage scores for credit insurance submissions to prioritize underwriting review. "
                "Scores are based on exposure limits, debtor days, financial documentation, trading history, "
                "broker quality, and risk factors like outstanding judgements."
)
async def triage_underwriting(batch: BatchSubmissions) -> List[TriageScore]:
    """
    Triage submissions for underwriting priority.
    
    Returns triage scores (0-1, higher is better) with explanatory reasons
    for each submission to help prioritize underwriting review.
    """
    # Convert submissions to list of dicts for processing
    submissions_data = [submission.model_dump() for submission in batch.submissions]
    
    # Prepare features
    submissions_df = prepare_submissions_features(submissions_data)
    
    # Calculate triage scores
    result = triage_scores(submissions_df)
    
    # Convert to response models
    return [TriageScore(**score) for score in result["scores"]]


@app.post(
    "/renewals/priority",
    response_model=List[TriageScore],
    summary="Renewal Priority",
    description="Calculate priority scores for policy renewals based on expiry dates, utilization rates, "
                "claims history, and client requests. Higher scores indicate more urgent renewal processing needs."
)
async def renewals_priority_endpoint(batch: BatchPolicies) -> List[TriageScore]:
    """
    Calculate renewal priority for policies.
    
    Returns priority scores (0-1, higher is more urgent) with explanatory reasons
    to help prioritize renewal processing and client outreach.
    """
    # Convert policies to list of dicts for processing
    policies_data = [policy.model_dump() for policy in batch.policies]
    
    # Prepare features
    policies_df = prepare_policies_features(policies_data)
    
    # Calculate renewal priorities
    result = renewals_priority(policies_df)
    
    # Convert to response models (reusing TriageScore for consistency)
    return [TriageScore(**priority) for priority in result["scores"]]


@app.post(
    "/pricing/suggest",
    response_model=List[PriceSuggestion],
    summary="Pricing Suggestions",
    description="Generate pricing suggestions for credit insurance submissions based on sector rates and "
                "risk adjustments. Returns suggested rates in basis points, risk bands, and detailed "
                "adjustments applied to the base sector rate."
)
async def pricing_suggest(batch: BatchSubmissions) -> List[PriceSuggestion]:
    """
    Generate pricing suggestions for submissions.
    
    Returns pricing suggestions with risk bands (A-E), suggested rates in basis points,
    base sector rates, and detailed adjustments applied based on risk factors.
    """
    # Convert submissions to list of dicts for processing
    submissions_data = [submission.model_dump() for submission in batch.submissions]
    
    # Prepare features
    submissions_df = prepare_submissions_features(submissions_data)
    
    # Generate pricing suggestions
    result = pricing_suggestions(submissions_df)
    
    # Convert to response models
    return [PriceSuggestion(**suggestion) for suggestion in result["suggestions"]]


@app.post(
    "/triage/underwriting/csv",
    response_model=List[TriageScore],
    summary="Underwriting Triage (CSV Upload)",
    description="Upload CSV file for underwriting triage. CSV must contain columns: submission_id, broker, sector, "
                "exposure_limit, debtor_days, financials_attached, years_trading, broker_hit_rate, "
                "requested_cov_pct, has_judgements. Boolean fields accept: true/false, 1/0, yes/no, y/n."
)
async def triage_underwriting_csv(file: UploadFile = File(...)) -> List[TriageScore]:
    """
    Triage submissions from CSV file for underwriting priority.
    
    Returns triage scores (0-1, higher is better) with explanatory reasons
    for each submission to help prioritize underwriting review.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        # Read and decode CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV to dictionaries
        csv_rows = parse_csv_to_dicts(csv_content)
        
        if not csv_rows:
            raise HTTPException(status_code=400, detail="CSV file is empty or has no data rows")
        
        # Validate required columns
        validate_csv_columns(csv_rows[0].keys(), SUBMISSION_COLUMNS, "submissions")
        
        # Convert CSV rows to submission dictionaries
        submissions_data = []
        for i, row in enumerate(csv_rows, 1):
            try:
                submission = convert_submission_row(row)
                submissions_data.append(submission)
            except (ValueError, KeyError) as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error parsing row {i}: {str(e)}. Please check data types and required fields."
                )
        
        # Prepare features and calculate triage scores
        submissions_df = prepare_submissions_features(submissions_data)
        result = triage_scores(submissions_df)
        
        # Convert to response models
        return [TriageScore(**score) for score in result["scores"]]
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV file: {str(e)}")


@app.post(
    "/renewals/priority/csv",
    response_model=List[TriageScore],
    summary="Renewal Priority (CSV Upload)",
    description="Upload CSV file for renewal priority scoring. CSV must contain columns: policy_id, sector, "
                "current_premium, limit, utilization_pct, claims_last_24m_cnt, claims_ratio_24m, "
                "days_to_expiry, requested_change_pct, broker."
)
async def renewals_priority_csv(file: UploadFile = File(...)) -> List[TriageScore]:
    """
    Calculate renewal priority from CSV file for policies.
    
    Returns priority scores (0-1, higher is more urgent) with explanatory reasons
    to help prioritize renewal processing and client outreach.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV file")
    
    try:
        # Read and decode CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Parse CSV to dictionaries
        csv_rows = parse_csv_to_dicts(csv_content)
        
        if not csv_rows:
            raise HTTPException(status_code=400, detail="CSV file is empty or has no data rows")
        
        # Validate required columns
        validate_csv_columns(csv_rows[0].keys(), POLICY_COLUMNS, "policies")
        
        # Convert CSV rows to policy dictionaries
        policies_data = []
        for i, row in enumerate(csv_rows, 1):
            try:
                policy = convert_policy_row(row)
                policies_data.append(policy)
            except (ValueError, KeyError) as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Error parsing row {i}: {str(e)}. Please check data types and required fields."
                )
        
        # Prepare features and calculate renewal priorities
        policies_df = prepare_policies_features(policies_data)
        result = renewals_priority(policies_df)
        
        # Convert to response models (reusing TriageScore for consistency)
        return [TriageScore(**priority) for priority in result["scores"]]
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing CSV file: {str(e)}")


@app.get("/", summary="Health Check", description="Simple health check endpoint")
async def root():
    """Health check endpoint."""
    return {"message": "CreditX API is running", "version": "1.0.0"}
