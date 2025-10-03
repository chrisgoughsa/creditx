"""Pricing logic for credit insurance submissions."""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple


def load_weights_config() -> Dict[str, any]:
    """Load weights configuration from YAML file."""
    weights_file = Path(__file__).parent.parent / "weights.yaml"
    with open(weights_file, 'r') as f:
        return yaml.safe_load(f)


# Load weights configuration
WEIGHTS_CONFIG = load_weights_config()


# Base sector rates in basis points (bps)
SECTOR_BASE_RATES: Dict[str, int] = {
    "Retail": 220,
    "Manufacturing": 260,
    "Logistics": 240,
    "Agri": 280,
    "Services": 200,
    "Other": 250,
}


def price_band(rate_bps: int) -> str:
    """
    Convert rate in basis points to risk band.
    
    Bands:
    - A: <=200 bps (lowest risk)
    - B: 201-250 bps
    - C: 251-300 bps
    - D: 301-360 bps
    - E: >360 bps (highest risk)
    """
    if rate_bps <= 200:
        return "A (<=200)"
    elif rate_bps <= 250:
        return "B (201-250)"
    elif rate_bps <= 300:
        return "C (251-300)"
    elif rate_bps <= 360:
        return "D (301-360)"
    else:
        return "E (>360)"


def suggest_rate(submission_row: Dict) -> Tuple[int, List[str]]:
    """
    Suggest pricing rate for a submission based on risk factors.
    
    Heuristics:
    - Start with sector base rate
    - Apply adjustments based on risk factors from weights.yaml configuration
    - Clip final rate between configured bounds
    
    Adjustments are loaded from weights.yaml configuration.
    """
    # Get configuration
    adjustments_config = WEIGHTS_CONFIG["pricing_adjustments"]
    bounds = WEIGHTS_CONFIG["pricing_bounds"]
    thresholds = WEIGHTS_CONFIG["thresholds"]
    
    # Start with sector base rate
    base_rate = SECTOR_BASE_RATES[submission_row["sector"]]
    rate = base_rate
    adjustments = []
    
    # Apply risk-based adjustments
    if submission_row["financials_attached"]:
        rate += adjustments_config["financials_attached"]
        adjustments.append(f"Financials attached ({adjustments_config['financials_attached']:+d} bps)")
    
    if submission_row["broker_hit_rate"] >= thresholds["broker_hit_rate_min"]:
        rate += adjustments_config["broker_hit_rate"]
        adjustments.append(f"Good broker track record ({adjustments_config['broker_hit_rate']:+d} bps)")
    
    if submission_row["debtor_days"] > thresholds["debtor_days_max"]:
        rate += adjustments_config["debtor_days"]
        adjustments.append(f"High debtor days (+{adjustments_config['debtor_days']} bps)")
    
    if submission_row["has_judgements"]:
        rate += adjustments_config["has_judgements"]
        adjustments.append(f"Outstanding judgements (+{adjustments_config['has_judgements']} bps)")
    
    if submission_row["requested_cov_pct"] > thresholds["high_coverage_min"]:
        rate += adjustments_config["high_coverage"]
        adjustments.append(f"High coverage request (+{adjustments_config['high_coverage']} bps)")
    
    if submission_row["years_trading"] < thresholds["limited_trading_max"]:
        rate += adjustments_config["limited_trading"]
        adjustments.append(f"Limited trading history (+{adjustments_config['limited_trading']} bps)")
    
    # Clip rate to configured bounds
    rate = max(bounds["min_rate"], min(bounds["max_rate"], rate))
    
    # Add clipping note if rate was adjusted
    if rate == bounds["min_rate"]:
        adjustments.append(f"Rate clipped to minimum ({bounds['min_rate']} bps)")
    elif rate == bounds["max_rate"]:
        adjustments.append(f"Rate clipped to maximum ({bounds['max_rate']} bps)")
    
    return rate, adjustments
