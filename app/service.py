"""Service layer for credit risk assessment and pricing."""

import polars as pl
from typing import List, Dict, Any

from .features import prepare_submissions_features, prepare_policies_features
from .pricing import suggest_rate, SECTOR_BASE_RATES


def triage_scores(submissions_df: pl.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculate triage scores for submissions based on weighted risk factors.
    
    Scoring weights:
    - 25% normalized exposure_limit (higher exposure = higher priority)
    - 20% (1 - debtor_days/180) (shorter debtor days = better)
    - 15% financials_attached flag (financials reduce uncertainty)
    - 15% years_trading/30 (more experience = better)
    - 15% broker_hit_rate (proven track record)
    - 10% (1 - judgements) (no judgements = better)
    
    Returns list of triage scores with reasons.
    """
    # Normalize exposure limit to 0-1 range (using log scale for better distribution)
    max_exposure = submissions_df["exposure_limit"].max()
    min_exposure = submissions_df["exposure_limit"].min()
    exposure_range = max_exposure - min_exposure if max_exposure > min_exposure else 1
    
    # Calculate weighted scores using vectorized operations
    scores = (
        0.25 * ((submissions_df["exposure_limit"] - min_exposure) / exposure_range) +
        0.20 * (1 - submissions_df["debtor_days"] / 180) +
        0.15 * submissions_df["financials_attached"] +
        0.15 * (submissions_df["years_trading"] / 30) +
        0.15 * submissions_df["broker_hit_rate"] +
        0.10 * (1 - submissions_df["has_judgements"])
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
    
    return results


def renewals_priority(policies_df: pl.DataFrame) -> List[Dict[str, Any]]:
    """
    Calculate renewal priority scores for policies based on weighted factors.
    
    Priority weights:
    - 35% (1 - days_to_expiry/365) (expiring soon = higher priority)
    - 25% utilization_pct (high utilization = higher priority)
    - 25% claims_ratio_24m clipped 0-2 / 2 (elevated loss ratio = higher priority)
    - 15% (-requested_change_pct) clipped to [-0.3, 0.3] (reduction request = higher priority)
    
    Returns list of priority scores with reasons.
    """
    # Calculate weighted priority scores using vectorized operations
    # Clip requested_change_pct to reasonable range for scoring
    change_pct_clipped = policies_df["requested_change_pct"].clip(-0.3, 0.3)
    
    priorities = (
        0.35 * (1 - policies_df["days_to_expiry"] / 365) +
        0.25 * policies_df["utilization_pct"] +
        0.25 * (policies_df["claims_ratio_24m"].clip(0, 2) / 2) +
        0.15 * (-change_pct_clipped)  # Negative because reduction requests increase priority
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
    
    return results


def pricing_suggestions(submissions_df: pl.DataFrame) -> List[Dict[str, Any]]:
    """
    Generate pricing suggestions for submissions.
    
    Applies suggest_rate function to each submission and returns
    pricing suggestions with risk bands and adjustments.
    """
    results = []
    
    for row in submissions_df.iter_rows(named=True):
        # Get suggested rate and adjustments
        suggested_rate, adjustments = suggest_rate(row)
        
        # Get base rate for the sector
        base_rate = SECTOR_BASE_RATES[row["sector"]]
        
        # Determine risk band
        from .pricing import price_band
        band = price_band(suggested_rate)
        
        results.append({
            "id": row["submission_id"],
            "band": band,
            "suggested_rate_bps": suggested_rate,
            "base_rate_bps": base_rate,
            "adjustments": adjustments
        })
    
    return results
