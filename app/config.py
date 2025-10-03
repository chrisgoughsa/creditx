"""Application configuration and weights loading utilities."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic.config import ConfigDict


class TriageWeights(BaseModel):
    exposure_limit: float
    debtor_days: float
    financials_attached: float
    years_trading: float
    broker_hit_rate: float
    has_judgements: float


class RenewalWeights(BaseModel):
    days_to_expiry: float
    utilization_pct: float
    claims_ratio_24m: float
    requested_change_pct: float


class PricingAdjustments(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    financials_attached: int = Field(alias="financials_attached")
    broker_hit_rate: int
    debtor_days: int
    has_judgements: int
    high_coverage: int
    limited_trading: int


class PricingBounds(BaseModel):
    min_rate: int
    max_rate: int


class Thresholds(BaseModel):
    broker_hit_rate_min: float
    debtor_days_max: float
    high_coverage_min: float
    limited_trading_max: float
    debtor_days_normalization: float
    years_trading_normalization: float
    claims_ratio_max: float
    change_pct_min: float
    change_pct_max: float


class BrokerScoreCurve(BaseModel):
    description: str
    adjustment_bps: int


class WeightsConfig(BaseModel):
    version: str
    triage_weights: TriageWeights
    renewals_weights: RenewalWeights
    pricing_adjustments: PricingAdjustments
    pricing_bounds: PricingBounds
    thresholds: Thresholds
    broker_score_curves: Dict[str, BrokerScoreCurve]
    sector_coverage_limits: Dict[str, float]

    @field_validator("version")
    @classmethod
    def non_empty_version(cls, value: str) -> str:
        if not value.strip():
            msg = "Weights configuration version must be a non-empty string"
            raise ValueError(msg)
        return value


def _default_weights_path() -> Path:
    return Path(__file__).parent.parent / "weights.yaml"


@lru_cache(maxsize=1)
def get_weights_config(path: Optional[Path] = None) -> WeightsConfig:
    """Load and cache weight configuration from YAML file."""
    weights_path = path or _default_weights_path()
    with weights_path.open("r", encoding="utf-8") as handle:
        raw_config = yaml.safe_load(handle)
    return WeightsConfig.model_validate(raw_config)


def reload_weights(path: Optional[Path] = None) -> WeightsConfig:
    """Clear cached weights and reload from disk."""
    get_weights_config.cache_clear()
    return get_weights_config(path)


__all__ = [
    "WeightsConfig",
    "TriageWeights",
    "RenewalWeights",
    "PricingAdjustments",
    "PricingBounds",
    "Thresholds",
    "BrokerScoreCurve",
    "get_weights_config",
    "reload_weights",
]
