"""Application configuration and weights loading utilities."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel, Field, validator


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
    financials_attached: int = Field(alias="financials_attached")
    broker_hit_rate: int
    debtor_days: int
    has_judgements: int
    high_coverage: int
    limited_trading: int

    class Config:
        populate_by_name = True


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


class WeightsConfig(BaseModel):
    version: str
    triage_weights: TriageWeights
    renewals_weights: RenewalWeights
    pricing_adjustments: PricingAdjustments
    pricing_bounds: PricingBounds
    thresholds: Thresholds

    @validator("version")
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


__all__ = [
    "WeightsConfig",
    "TriageWeights",
    "RenewalWeights",
    "PricingAdjustments",
    "PricingBounds",
    "Thresholds",
    "get_weights_config",
]
