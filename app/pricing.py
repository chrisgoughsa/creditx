"""Pricing logic for credit insurance submissions."""

from typing import Dict, List, Tuple


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
    - Apply adjustments based on risk factors
    - Clip final rate between 120-500 bps
    
    Adjustments:
    - -15 bps if financials_attached (reduces uncertainty)
    - -10 bps if broker_hit_rate >= 0.5 (proven track record)
    - +25 bps if debtor_days > 75 (higher credit risk)
    - +60 bps if has_judgements (significant risk factor)
    - +20 bps if requested_cov_pct > 0.9 (high coverage request)
    - +30 bps if years_trading < 2 (inexperienced business)
    """
    # Start with sector base rate
    base_rate = SECTOR_BASE_RATES[submission_row["sector"]]
    rate = base_rate
    adjustments = []
    
    # Apply risk-based adjustments
    if submission_row["financials_attached"]:
        rate -= 15
        adjustments.append("Financials attached (-15 bps)")
    
    if submission_row["broker_hit_rate"] >= 0.5:
        rate -= 10
        adjustments.append("Good broker track record (-10 bps)")
    
    if submission_row["debtor_days"] > 75:
        rate += 25
        adjustments.append("High debtor days (+25 bps)")
    
    if submission_row["has_judgements"]:
        rate += 60
        adjustments.append("Outstanding judgements (+60 bps)")
    
    if submission_row["requested_cov_pct"] > 0.9:
        rate += 20
        adjustments.append("High coverage request (+20 bps)")
    
    if submission_row["years_trading"] < 2:
        rate += 30
        adjustments.append("Limited trading history (+30 bps)")
    
    # Clip rate to reasonable bounds (120-500 bps)
    rate = max(120, min(500, rate))
    
    # Add clipping note if rate was adjusted
    if rate == 120:
        adjustments.append("Rate clipped to minimum (120 bps)")
    elif rate == 500:
        adjustments.append("Rate clipped to maximum (500 bps)")
    
    return rate, adjustments
