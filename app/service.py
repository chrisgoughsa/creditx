"""Service layer for credit risk assessment and pricing."""

from __future__ import annotations

from typing import Any, Dict, List

import polars as pl

from .config import get_weights_config
from .features import prepare_policies_features, prepare_submissions_features
from .pricing import SECTOR_BASE_RATES, price_band, suggest_rate


def triage_scores(submissions_df: pl.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculate triage scores for submissions based on weighted risk factors.
    
    Scoring weights are loaded from weights.yaml configuration.
    
    Returns list of triage scores with reasons and weights version.
    """
    config = get_weights_config()
    weights = config.triage_weights
    thresholds = config.thresholds
    
    # Normalize exposure limit to 0-1 range (using log scale for better distribution)
    max_exposure = submissions_df["exposure_limit"].max()
    min_exposure = submissions_df["exposure_limit"].min()
    exposure_range = max_exposure - min_exposure if max_exposure > min_exposure else 1
    
    # Calculate weighted scores using vectorized operations
    scores = (
        weights.exposure_limit
        * ((submissions_df["exposure_limit"] - min_exposure) / exposure_range)
        + weights.debtor_days
        * (1 - submissions_df["debtor_days"] / thresholds.debtor_days_normalization)
        + weights.financials_attached
        * submissions_df["financials_attached"].cast(pl.Float64)
        + weights.years_trading
        * (submissions_df["years_trading"] / thresholds.years_trading_normalization)
        + weights.broker_hit_rate * submissions_df["broker_hit_rate"]
        + weights.has_judgements
        * (1 - submissions_df["has_judgements"].cast(pl.Float64))
    )
    
    # Clip scores to 0-1 range
    scores = scores.clip(0, 1)
    
    # Generate reasons for each submission
    results = []
    for i, row in enumerate(submissions_df.iter_rows(named=True)):
        reasons = []
        
        # Add reasons based on contributing factors
        if row["financials_attached"]:
            reasons.append("Financial statements provided")
        
        if row["broker_hit_rate"] >= 0.5:
            reasons.append("Good broker quality track record")
        
        if row["debtor_days"] <= 60:
            reasons.append("Short debtor days")
        elif row["debtor_days"] > 120:
            reasons.append("Long debtor days warning")
        
        if row["has_judgements"]:
            reasons.append("Outstanding judgements warning")
        
        if row["years_trading"] < 2:
            reasons.append("Limited trading history")
        elif row["years_trading"] >= 10:
            reasons.append("Established trading history")
        
        results.append({
            "id": row["submission_id"],
            "score": float(scores[i]),
            "reasons": reasons
        })
    
    return {
        "scores": results,
        "weights_version": config.version,
    }


def renewals_priority(policies_df: pl.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculate renewal priority scores for policies based on weighted factors.
    
    Priority weights are loaded from weights.yaml configuration.
    
    Returns list of priority scores with reasons and weights version.
    """
    config = get_weights_config()
    weights = config.renewals_weights
    thresholds = config.thresholds
    
    # Calculate weighted priority scores using vectorized operations
    # Clip requested_change_pct to reasonable range for scoring
    change_pct_clipped = policies_df["requested_change_pct"].clip(
        thresholds["change_pct_min"], 
        thresholds["change_pct_max"]
    )
    
    priorities = (
        weights.days_to_expiry * (1 - policies_df["days_to_expiry"] / 365)
        + weights.utilization_pct * policies_df["utilization_pct"]
        + weights.claims_ratio_24m
        * (
            policies_df["claims_ratio_24m"].clip(0, thresholds.claims_ratio_max)
            / thresholds.claims_ratio_max
        )
        + weights.requested_change_pct * (-change_pct_clipped)
    )
    
    # Clip priorities to 0-1 range
    priorities = priorities.clip(0, 1)
    
    # Generate reasons for each policy
    results = []
    for i, row in enumerate(policies_df.iter_rows(named=True)):
        reasons = []
        
        # Add reasons based on contributing factors
        if row["days_to_expiry"] <= 30:
            reasons.append("Expiring within 30 days")
        elif row["days_to_expiry"] <= 90:
            reasons.append("Expiring soon")
        
        if row["utilization_pct"] >= 0.8:
            reasons.append("High utilization")
        elif row["utilization_pct"] <= 0.3:
            reasons.append("Low utilization")
        
        if row["claims_ratio_24m"] >= 1.5:
            reasons.append("Elevated loss ratio")
        elif row["claims_ratio_24m"] <= 0.5:
            reasons.append("Low loss ratio")
        
        if row["requested_change_pct"] < -0.1:
            reasons.append("Client requesting significant reduction")
        elif row["requested_change_pct"] > 0.1:
            reasons.append("Client requesting increase")
        
        results.append({
            "id": row["policy_id"],
            "score": float(priorities[i]),
            "reasons": reasons
        })
    
    return {
        "scores": results,
        "weights_version": config.version,
    }


def pricing_suggestions(submissions_df: pl.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate pricing suggestions for submissions.
    
    Applies suggest_rate function to each submission and returns
    pricing suggestions with risk bands and adjustments.
    """
    config = get_weights_config()
    results = []
    
    for row in submissions_df.iter_rows(named=True):
        # Get suggested rate and adjustments
        suggested_rate, adjustments = suggest_rate(row)
        
        # Get base rate for the sector
        base_rate = SECTOR_BASE_RATES[row["sector"]]
        band = price_band(suggested_rate)
        
        results.append({
            "id": row["submission_id"],
            "band_code": band.code,
            "band_label": band.label,
            "band_description": band.description,
            "suggested_rate_bps": suggested_rate,
            "base_rate_bps": base_rate,
            "adjustments": adjustments
        })
    
    return {
        "suggestions": results,
        "weights_version": config.version,
    }
