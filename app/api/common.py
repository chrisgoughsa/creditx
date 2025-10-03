"""Shared helpers for API routes."""

from __future__ import annotations

import csv
import io
from typing import Any, Callable, Dict, Iterable, List, Set

from fastapi import HTTPException, UploadFile

TRUE_VALUES = {"true", "1", "yes", "y"}
FALSE_VALUES = {"false", "0", "no", "n"}


SUBMISSION_COLUMNS: Set[str] = {
    "submission_id",
    "broker",
    "sector",
    "exposure_limit",
    "debtor_days",
    "financials_attached",
    "years_trading",
    "broker_hit_rate",
    "requested_cov_pct",
    "has_judgements",
}

POLICY_COLUMNS: Set[str] = {
    "policy_id",
    "sector",
    "current_premium",
    "limit",
    "utilization_pct",
    "claims_last_24m_cnt",
    "claims_ratio_24m",
    "days_to_expiry",
    "requested_change_pct",
    "broker",
}


def validate_csv_columns(columns: Iterable[str], required_columns: Set[str], file_type: str) -> None:
    """Validate that CSV has all required columns."""
    missing_columns = required_columns - set(columns)
    if missing_columns:
        required = ", ".join(sorted(required_columns))
        missing = ", ".join(sorted(missing_columns))
        raise HTTPException(
            status_code=400,
            detail=(
                f"Missing required columns in {file_type} CSV: {missing}. "
                f"Required columns: {required}"
            ),
        )


def parse_bool(value: str) -> bool:
    """Parse relaxed boolean values used in CSV uploads."""
    lowered = value.strip().lower()
    if lowered in TRUE_VALUES:
        return True
    if lowered in FALSE_VALUES:
        return False
    # Fall back to earlier behaviour: treat unknown values as False
    return False


def convert_submission_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Convert CSV row to submission dictionary with proper types."""
    for field in SUBMISSION_COLUMNS:
        if field not in row or row[field] is None or row[field].strip() == "":
            raise KeyError(f"Missing required field: {field}")

    return {
        "submission_id": row["submission_id"],
        "broker": row["broker"],
        "sector": row["sector"],
        "exposure_limit": float(row["exposure_limit"]),
        "debtor_days": float(row["debtor_days"]),
        "financials_attached": parse_bool(row["financials_attached"]),
        "years_trading": float(row["years_trading"]),
        "broker_hit_rate": float(row["broker_hit_rate"]),
        "requested_cov_pct": float(row["requested_cov_pct"]),
        "has_judgements": parse_bool(row["has_judgements"]),
    }


def convert_policy_row(row: Dict[str, str]) -> Dict[str, Any]:
    """Convert CSV row to policy dictionary with proper types."""
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
        "broker": row["broker"],
    }


async def parse_csv_upload(
    file: UploadFile,
    *,
    required_columns: Set[str],
    file_type: str,
    row_converter: Callable[[Dict[str, str]], Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Parse CSV uploads using a streamed reader and row converter."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV file")

    try:
        file.file.seek(0)
    except (AttributeError, OSError):
        # Some backends may not support seek; ignore best-effort
        pass

    try:
        wrapper = io.TextIOWrapper(file.file, encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded") from exc

    try:
        reader = csv.DictReader(wrapper)
        headers = reader.fieldnames
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded") from exc

    if headers is None:
        raise HTTPException(status_code=400, detail="CSV file is empty or missing a header row")

    validate_csv_columns(headers, required_columns, file_type)

    records: List[Dict[str, Any]] = []
    try:
        for index, row in enumerate(reader, start=1):
            if not row:
                continue
            try:
                records.append(row_converter(row))
            except (ValueError, KeyError) as exc:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Error parsing row {index}: {exc}. Please check data types and required fields."
                    ),
                ) from exc
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded") from exc

    if not records:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no data rows")

    try:
        wrapper.detach()
    except Exception:
        # Detach is best-effort; ignore if not supported
        pass

    return records


__all__ = [
    "SUBMISSION_COLUMNS",
    "POLICY_COLUMNS",
    "validate_csv_columns",
    "parse_csv_upload",
    "convert_submission_row",
    "convert_policy_row",
]
