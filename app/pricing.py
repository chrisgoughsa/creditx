"""Pricing logic for credit insurance submissions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, TypedDict

from .config import get_weights_config
from .data_cache import cache_pricing


# Base sector rates in basis points (bps)
SECTOR_BASE_RATES: Dict[str, int] = {
    "Retail": 220,
    "Manufacturing": 260,
    "Logistics": 240,
    "Agri": 280,
    "Services": 200,
    "Other": 250,
}


class SubmissionFeatures(TypedDict):
    submission_id: str
    broker: str
    sector: str
    exposure_limit: float
    debtor_days: float
    financials_attached: bool
    years_trading: float
    broker_hit_rate: float
    requested_cov_pct: float
    has_judgements: bool


@dataclass(frozen=True)
class PriceBand:
    code: str
    label: str
    description: str


PRICE_BANDS: Tuple[PriceBand, ...] = (
    PriceBand("A", "<=200 bps", "Lowest risk submissions"),
    PriceBand("B", "201-250 bps", "Low risk submissions"),
    PriceBand("C", "251-300 bps", "Moderate risk submissions"),
    PriceBand("D", "301-360 bps", "Elevated risk submissions"),
    PriceBand("E", ">360 bps", "Highest risk submissions"),
)


def price_band(rate_bps: int) -> PriceBand:
    """Convert rate in basis points to a structured risk band."""
    if rate_bps <= 200:
        return PRICE_BANDS[0]
    if rate_bps <= 250:
        return PRICE_BANDS[1]
    if rate_bps <= 300:
        return PRICE_BANDS[2]
    if rate_bps <= 360:
        return PRICE_BANDS[3]
    return PRICE_BANDS[4]


@cache_pricing
def _suggest_rate_cached(
    sector: str,
    financials_attached: bool,
    broker_hit_rate: float,
    debtor_days: float,
    has_judgements: bool,
    requested_cov_pct: float,
    years_trading: float,
) -> Tuple[int, Tuple[str, ...]]:
    """
    Suggest pricing rate for a submission based on risk factors.
    
    Heuristics:
    - Start with sector base rate
    - Apply adjustments based on risk factors from weights.yaml configuration
    - Clip final rate between configured bounds
    
    Adjustments are loaded from weights.yaml configuration.
    """
    # Get configuration
    weights_config = get_weights_config()
    adjustments_config = weights_config.pricing_adjustments
    bounds = weights_config.pricing_bounds
    thresholds = weights_config.thresholds
    
    # Start with sector base rate
    base_rate = SECTOR_BASE_RATES[sector]
    rate = base_rate
    adjustments = []
    
    # Apply risk-based adjustments
    if financials_attached:
        rate += adjustments_config.financials_attached
        adjustments.append(
            f"Financials attached ({adjustments_config.financials_attached:+d} bps)"
        )

    if broker_hit_rate >= thresholds.broker_hit_rate_min:
        rate += adjustments_config.broker_hit_rate
        adjustments.append(
            f"Good broker track record ({adjustments_config.broker_hit_rate:+d} bps)"
        )

    if debtor_days > thresholds.debtor_days_max:
        rate += adjustments_config.debtor_days
        adjustments.append(
            f"High debtor days (+{adjustments_config.debtor_days} bps)"
        )

    if has_judgements:
        rate += adjustments_config.has_judgements
        adjustments.append(
            f"Outstanding judgements (+{adjustments_config.has_judgements} bps)"
        )

    if requested_cov_pct > thresholds.high_coverage_min:
        rate += adjustments_config.high_coverage
        adjustments.append(
            f"High coverage request (+{adjustments_config.high_coverage} bps)"
        )

    if years_trading < thresholds.limited_trading_max:
        rate += adjustments_config.limited_trading
        adjustments.append(
            f"Limited trading history (+{adjustments_config.limited_trading} bps)"
        )

    # Clip rate to configured bounds
    rate = max(bounds.min_rate, min(bounds.max_rate, rate))

    # Add clipping note if rate was adjusted
    if rate == bounds.min_rate:
        adjustments.append(f"Rate clipped to minimum ({bounds.min_rate} bps)")
    elif rate == bounds.max_rate:
        adjustments.append(f"Rate clipped to maximum ({bounds.max_rate} bps)")

    return rate, tuple(adjustments)


def suggest_rate(submission_row: SubmissionFeatures) -> Tuple[int, List[str]]:
    """Wrapper around cached pricing computation."""
    rate, adjustments = _suggest_rate_cached(
        submission_row["sector"],
        submission_row["financials_attached"],
        submission_row["broker_hit_rate"],
        submission_row["debtor_days"],
        submission_row["has_judgements"],
        submission_row["requested_cov_pct"],
        submission_row["years_trading"],
    )
    return rate, list(adjustments)
