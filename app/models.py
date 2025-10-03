"""Pydantic models for credit risk assessment and pricing system."""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Submission(BaseModel):
    """Credit insurance submission model."""
    
    submission_id: str
    broker: str
    sector: Literal["Retail", "Manufacturing", "Logistics", "Agri", "Services", "Other"]
    exposure_limit: float = Field(ge=0, description="Exposure limit in currency units")
    debtor_days: float = Field(ge=0, description="Debtor days (0-180)")
    financials_attached: bool = Field(description="Whether financial statements are attached")
    years_trading: float = Field(ge=0, description="Years of trading experience (0-30)")
    broker_hit_rate: float = Field(ge=0, le=1, description="Broker success rate (0-1)")
    requested_cov_pct: float = Field(ge=0, le=1, description="Requested coverage percentage (0-1)")
    has_judgements: bool = Field(description="Whether debtor has outstanding judgements")


class Policy(BaseModel):
    """Credit insurance policy model."""
    
    policy_id: str
    sector: Literal["Retail", "Manufacturing", "Logistics", "Agri", "Services", "Other"]
    current_premium: float = Field(ge=0, description="Current premium in currency units")
    limit: float = Field(ge=0, description="Policy limit in currency units")
    utilization_pct: float = Field(ge=0, le=1, description="Utilization percentage (0-1)")
    claims_last_24m_cnt: int = Field(ge=0, description="Claims count in last 24 months")
    claims_ratio_24m: float = Field(ge=0, description="Claims ratio in last 24 months")
    days_to_expiry: float = Field(ge=0, description="Days until policy expiry (0-365)")
    requested_change_pct: float = Field(description="Requested premium change percentage (e.g., -0.1 for 10% reduction)")
    broker: str


class BatchSubmissions(BaseModel):
    """Batch of credit insurance submissions."""
    
    submissions: List[Submission]


class BatchPolicies(BaseModel):
    """Batch of credit insurance policies."""
    
    policies: List[Policy]


class TriageScore(BaseModel):
    """Triage scoring result."""
    
    id: str
    score: float = Field(ge=0, le=1, description="Triage score (0-1, higher is better)")
    reasons: List[str] = Field(description="List of reasons explaining the score")


class PriceSuggestion(BaseModel):
    """Pricing suggestion result."""

    id: str
    band_code: Literal["A", "B", "C", "D", "E"] = Field(
        description="Risk band code"
    )
    band_label: str = Field(description="Human-readable band label")
    band_description: str = Field(description="Band description for UI copy")
    suggested_rate_bps: int = Field(ge=0, description="Suggested rate in basis points")
    base_rate_bps: int = Field(ge=0, description="Base sector rate in basis points")
    adjustments: List[str] = Field(description="List of adjustments applied")
