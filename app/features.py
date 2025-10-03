"""Feature engineering for credit risk assessment and pricing system."""

import polars as pl
from typing import List, Dict, Any


def prepare_submissions_features(submissions: List[Dict[str, Any]]) -> pl.DataFrame:
    """
    Convert submissions list to Polars DataFrame and engineer features.
    
    Features engineered:
    - financials_attached: Binary flag (0/1)
    - debtor_days: Clipped to 0-180 range
    - years_trading: Clipped to 0-30 range
    - has_judgements: Binary flag (0/1)
    - log_expo: Log1p of exposure_limit for better scaling
    """
    # Convert to Polars DataFrame
    df = pl.DataFrame(submissions)
    
    # Engineer features with vectorized operations
    df = df.with_columns([
        # Binary flags for boolean fields
        pl.col("financials_attached").cast(pl.Int8).alias("financials_attached"),
        pl.col("has_judgements").cast(pl.Int8).alias("has_judgements"),
        
        # Clip numeric fields to reasonable ranges
        pl.col("debtor_days").clip(0, 180).alias("debtor_days"),
        pl.col("years_trading").clip(0, 30).alias("years_trading"),
        
        # Log transform exposure limit for better scaling
        pl.col("exposure_limit").log1p().alias("log_expo"),
    ])
    
    return df


def prepare_policies_features(policies: List[Dict[str, Any]]) -> pl.DataFrame:
    """
    Convert policies list to Polars DataFrame and engineer features.
    
    Features engineered:
    - utilization_pct: Clipped to 0-1 range
    - claims_ratio_24m: Clipped to 0-5 range
    - days_to_expiry: Clipped to 0-365 range
    """
    # Convert to Polars DataFrame
    df = pl.DataFrame(policies)
    
    # Engineer features with vectorized operations
    df = df.with_columns([
        # Clip numeric fields to reasonable ranges
        pl.col("utilization_pct").clip(0, 1).alias("utilization_pct"),
        pl.col("claims_ratio_24m").clip(0, 5).alias("claims_ratio_24m"),
        pl.col("days_to_expiry").clip(0, 365).alias("days_to_expiry"),
    ])
    
    return df
