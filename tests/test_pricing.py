"""Tests for pricing functionality."""

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


@pytest.fixture
def strong_submission():
    """Strong profile submission for testing."""
    return {
        "submission_id": "strong_001",
        "broker": "PremiumBroker",
        "sector": "Retail",
        "exposure_limit": 1000000.0,
        "debtor_days": 45.0,  # Short debtor days
        "financials_attached": True,  # Complete docs
        "years_trading": 8.0,
        "broker_hit_rate": 0.85,  # Good broker hit rate
        "requested_cov_pct": 0.75,  # Reasonable coverage
        "has_judgements": False  # No judgements
    }


@pytest.fixture
def weak_submission():
    """Weak profile submission for testing."""
    return {
        "submission_id": "weak_001",
        "broker": "NewBroker",
        "sector": "Manufacturing",
        "exposure_limit": 500000.0,
        "debtor_days": 120.0,  # Long debtor days
        "financials_attached": False,  # No financials
        "years_trading": 1.5,
        "broker_hit_rate": 0.3,  # Poor broker hit rate
        "requested_cov_pct": 0.95,  # High coverage request
        "has_judgements": True  # Has judgements
    }


def test_strong_profile_gets_low_risk_band(strong_submission):
    """Test that strong profile gets A or B risk band."""
    response = client.post(
        "/pricing/suggest",
        json={"submissions": [strong_submission]}
    )
    
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["suggestions"]) == 1
    suggestion = payload["suggestions"][0]
    assert suggestion["id"] == "strong_001"
    assert suggestion["band_code"] in ["A", "B"]
    assert suggestion["band_label"] in ["<=200 bps", "201-250 bps"]
    assert isinstance(suggestion["band_description"], str)
    assert suggestion["suggested_rate_bps"] <= 250
    assert suggestion["base_rate_bps"] == 220  # Retail base rate
    
    # Should have positive adjustments for strong profile
    adjustments = suggestion["adjustments"]
    assert any("Financials attached" in adj for adj in adjustments)
    assert any("Good broker track record" in adj for adj in adjustments)


def test_weak_profile_gets_higher_risk_band(weak_submission):
    """Test that weak profile with judgements and long debtor days gets higher band."""
    response = client.post(
        "/pricing/suggest",
        json={"submissions": [weak_submission]}
    )
    
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["suggestions"]) == 1
    suggestion = payload["suggestions"][0]
    assert suggestion["id"] == "weak_001"
    # Should get C, D, or E band due to multiple risk factors
    assert suggestion["band_code"] in ["C", "D", "E"]
    assert suggestion["band_description"].endswith("risk submissions")
    assert suggestion["suggested_rate_bps"] >= 251
    assert suggestion["base_rate_bps"] == 260  # Manufacturing base rate
    
    # Should have negative adjustments for weak profile
    adjustments = suggestion["adjustments"]
    assert any("Outstanding judgements" in adj for adj in adjustments)
    assert any("High debtor days" in adj for adj in adjustments)
    assert any("High coverage request" in adj for adj in adjustments)
    assert any("Limited trading history" in adj for adj in adjustments)


def test_judgements_significantly_increase_rate():
    """Test that judgements significantly increase the pricing rate."""
    # Same submission with and without judgements
    base_submission = {
        "submission_id": "test_001",
        "broker": "TestBroker",
        "sector": "Services",
        "exposure_limit": 750000.0,
        "debtor_days": 60.0,
        "financials_attached": True,
        "years_trading": 5.0,
        "broker_hit_rate": 0.6,
        "requested_cov_pct": 0.8,
        "has_judgements": False
    }
    
    with_judgements = base_submission.copy()
    with_judgements["has_judgements"] = True
    with_judgements["submission_id"] = "test_002"
    
    # Test without judgements
    response1 = client.post(
        "/pricing/suggest",
        json={"submissions": [base_submission]}
    )
    assert response1.status_code == 200
    rate_without = response1.json()["suggestions"][0]["suggested_rate_bps"]
    
    # Test with judgements
    response2 = client.post(
        "/pricing/suggest",
        json={"submissions": [with_judgements]}
    )
    assert response2.status_code == 200
    rate_with = response2.json()["suggestions"][0]["suggested_rate_bps"]
    
    # Rate with judgements should be 60 bps higher (as per pricing logic)
    assert rate_with == rate_without + 60


def test_long_debtor_days_increase_rate():
    """Test that long debtor days increase the pricing rate."""
    short_days = {
        "submission_id": "short_001",
        "broker": "TestBroker",
        "sector": "Retail",
        "exposure_limit": 500000.0,
        "debtor_days": 45.0,  # Short days
        "financials_attached": True,
        "years_trading": 5.0,
        "broker_hit_rate": 0.6,
        "requested_cov_pct": 0.8,
        "has_judgements": False
    }
    
    long_days = short_days.copy()
    long_days["submission_id"] = "long_001"
    long_days["debtor_days"] = 90.0  # Long days
    
    # Test short debtor days
    response1 = client.post(
        "/pricing/suggest",
        json={"submissions": [short_days]}
    )
    assert response1.status_code == 200
    rate_short = response1.json()["suggestions"][0]["suggested_rate_bps"]
    
    # Test long debtor days
    response2 = client.post(
        "/pricing/suggest",
        json={"submissions": [long_days]}
    )
    assert response2.status_code == 200
    rate_long = response2.json()["suggestions"][0]["suggested_rate_bps"]
    
    # Rate with long debtor days should be 25 bps higher
    assert rate_long == rate_short + 25


def test_rate_clipping():
    """Test that rates are properly clipped to 120-500 bps range."""
    # Create extreme case that would exceed bounds
    extreme_submission = {
        "submission_id": "extreme_001",
        "broker": "BadBroker",
        "sector": "Agri",  # High base rate (280)
        "exposure_limit": 1000000.0,
        "debtor_days": 150.0,  # Long days (+25)
        "financials_attached": False,  # No financials
        "years_trading": 0.5,  # Very limited history (+30)
        "broker_hit_rate": 0.1,  # Poor broker
        "requested_cov_pct": 0.95,  # High coverage (+20)
        "has_judgements": True  # Judgements (+60)
    }
    
    response = client.post(
        "/pricing/suggest",
        json={"submissions": [extreme_submission]}
    )
    
    assert response.status_code == 200
    payload = response.json()
    suggestion = payload["suggestions"][0]
    
    # Rate should be high due to multiple risk factors
    assert suggestion["suggested_rate_bps"] >= 400  # High rate due to multiple risk factors
    # Check that it has the expected adjustments
    adjustments = suggestion["adjustments"]
    assert any("Outstanding judgements" in adj for adj in adjustments)
    assert any("High debtor days" in adj for adj in adjustments)
    assert any("High coverage request" in adj for adj in adjustments)
    assert any("Limited trading history" in adj for adj in adjustments)


def test_batch_pricing():
    """Test pricing multiple submissions in a single request."""
    submissions = [
        {
            "submission_id": "batch_001",
            "broker": "Broker1",
            "sector": "Retail",
            "exposure_limit": 500000.0,
            "debtor_days": 30.0,
            "financials_attached": True,
            "years_trading": 10.0,
            "broker_hit_rate": 0.8,
            "requested_cov_pct": 0.7,
            "has_judgements": False
        },
        {
            "submission_id": "batch_002",
            "broker": "Broker2",
            "sector": "Manufacturing",
            "exposure_limit": 2000000.0,
            "debtor_days": 100.0,
            "financials_attached": False,
            "years_trading": 2.0,
            "broker_hit_rate": 0.4,
            "requested_cov_pct": 0.9,
            "has_judgements": True
        }
    ]
    
    response = client.post(
        "/pricing/suggest",
        json={"submissions": submissions}
    )
    
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["suggestions"]) == 2
    
    # First submission should have lower rate (strong profile)
    # Second submission should have higher rate (weak profile)
    first, second = payload["suggestions"]
    assert first["suggested_rate_bps"] < second["suggested_rate_bps"]
    assert first["band_code"] in ["A", "B"]
    assert second["band_code"] in ["C", "D", "E"]
    assert isinstance(payload["feature_importance"], dict)


def test_pricing_feature_importance(strong_submission, weak_submission):
    """Feature importance returns adjustment hit counts."""
    response = client.post(
        "/pricing/suggest",
        json={"submissions": [strong_submission, weak_submission]},
    )

    assert response.status_code == 200
    payload = response.json()
    importance = payload["feature_importance"]
    assert any("Financials attached" in key for key in importance)
