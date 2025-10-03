"""Tests for triage functionality."""

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


@pytest.fixture
def high_priority_submission():
    """High priority submission with complete docs and short debtor days."""
    return {
        "submission_id": "high_001",
        "broker": "PremiumBroker",
        "sector": "Retail",
        "exposure_limit": 2000000.0,  # High exposure
        "debtor_days": 30.0,  # Short debtor days
        "financials_attached": True,  # Complete docs
        "years_trading": 15.0,  # Established business
        "broker_hit_rate": 0.9,  # Excellent broker
        "requested_cov_pct": 0.8,
        "has_judgements": False  # No judgements
    }


@pytest.fixture
def low_priority_submission():
    """Low priority submission with incomplete docs and long debtor days."""
    return {
        "submission_id": "low_001",
        "broker": "NewBroker",
        "sector": "Services",
        "exposure_limit": 200000.0,  # Lower exposure
        "debtor_days": 150.0,  # Long debtor days
        "financials_attached": False,  # Incomplete docs
        "years_trading": 1.0,  # New business
        "broker_hit_rate": 0.2,  # Poor broker
        "requested_cov_pct": 0.9,
        "has_judgements": True  # Has judgements
    }


def test_complete_docs_higher_score():
    """Test that submissions with complete docs get higher triage scores."""
    with_docs = {
        "submission_id": "with_docs_001",
        "broker": "TestBroker",
        "sector": "Retail",
        "exposure_limit": 1000000.0,
        "debtor_days": 60.0,
        "financials_attached": True,  # Complete docs
        "years_trading": 5.0,
        "broker_hit_rate": 0.6,
        "requested_cov_pct": 0.8,
        "has_judgements": False
    }
    
    without_docs = with_docs.copy()
    without_docs["submission_id"] = "without_docs_001"
    without_docs["financials_attached"] = False  # Incomplete docs
    
    # Test with docs
    response1 = client.post(
        "/triage/underwriting",
        json={"submissions": [with_docs]}
    )
    assert response1.status_code == 200
    score_with_docs = response1.json()[0]["score"]
    
    # Test without docs
    response2 = client.post(
        "/triage/underwriting",
        json={"submissions": [without_docs]}
    )
    assert response2.status_code == 200
    score_without_docs = response2.json()[0]["score"]
    
    # Score with docs should be higher
    assert score_with_docs > score_without_docs
    
    # Check that reasons include financial statements
    reasons_with_docs = response1.json()[0]["reasons"]
    assert "Financial statements provided" in reasons_with_docs


def test_shorter_debtor_days_higher_score():
    """Test that shorter debtor days result in higher triage scores."""
    short_days = {
        "submission_id": "short_001",
        "broker": "TestBroker",
        "sector": "Manufacturing",
        "exposure_limit": 1000000.0,
        "debtor_days": 30.0,  # Short debtor days
        "financials_attached": True,
        "years_trading": 5.0,
        "broker_hit_rate": 0.6,
        "requested_cov_pct": 0.8,
        "has_judgements": False
    }
    
    long_days = short_days.copy()
    long_days["submission_id"] = "long_001"
    long_days["debtor_days"] = 120.0  # Long debtor days
    
    # Test short debtor days
    response1 = client.post(
        "/triage/underwriting",
        json={"submissions": [short_days]}
    )
    assert response1.status_code == 200
    score_short = response1.json()[0]["score"]
    
    # Test long debtor days
    response2 = client.post(
        "/triage/underwriting",
        json={"submissions": [long_days]}
    )
    assert response2.status_code == 200
    score_long = response2.json()[0]["score"]
    
    # Score with short debtor days should be higher
    assert score_short > score_long
    
    # Check reasons
    reasons_short = response1.json()[0]["reasons"]
    reasons_long = response2.json()[0]["reasons"]
    assert "Short debtor days" in reasons_short
    # Long debtor days might not trigger warning if other factors are good
    # Just verify the score difference


def test_high_priority_submission_scoring(high_priority_submission):
    """Test that high priority submission gets high triage score."""
    response = client.post(
        "/triage/underwriting",
        json={"submissions": [high_priority_submission]}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    
    triage = data[0]
    assert triage["id"] == "high_001"
    assert triage["score"] > 0.6  # Should be high score
    
    # Should have positive reasons
    reasons = triage["reasons"]
    assert "Financial statements provided" in reasons
    assert "Good broker quality track record" in reasons
    assert "Short debtor days" in reasons
    assert "Established trading history" in reasons


def test_low_priority_submission_scoring(low_priority_submission):
    """Test that low priority submission gets low triage score."""
    response = client.post(
        "/triage/underwriting",
        json={"submissions": [low_priority_submission]}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    
    triage = data[0]
    assert triage["id"] == "low_001"
    assert triage["score"] < 0.5  # Should be low score
    
    # Should have warning reasons
    reasons = triage["reasons"]
    assert "Long debtor days warning" in reasons
    assert "Outstanding judgements warning" in reasons
    assert "Limited trading history" in reasons


def test_judgements_lower_score():
    """Test that judgements significantly lower the triage score."""
    no_judgements = {
        "submission_id": "no_judgements_001",
        "broker": "TestBroker",
        "sector": "Retail",
        "exposure_limit": 1000000.0,
        "debtor_days": 60.0,
        "financials_attached": True,
        "years_trading": 5.0,
        "broker_hit_rate": 0.6,
        "requested_cov_pct": 0.8,
        "has_judgements": False
    }
    
    with_judgements = no_judgements.copy()
    with_judgements["submission_id"] = "with_judgements_001"
    with_judgements["has_judgements"] = True
    
    # Test without judgements
    response1 = client.post(
        "/triage/underwriting",
        json={"submissions": [no_judgements]}
    )
    assert response1.status_code == 200
    score_no_judgements = response1.json()[0]["score"]
    
    # Test with judgements
    response2 = client.post(
        "/triage/underwriting",
        json={"submissions": [with_judgements]}
    )
    assert response2.status_code == 200
    score_with_judgements = response2.json()[0]["score"]
    
    # Score without judgements should be higher
    assert score_no_judgements > score_with_judgements
    
    # Check that judgements warning is in reasons
    reasons_with_judgements = response2.json()[0]["reasons"]
    assert "Outstanding judgements warning" in reasons_with_judgements


def test_broker_quality_affects_score():
    """Test that broker hit rate affects triage score."""
    good_broker = {
        "submission_id": "good_broker_001",
        "broker": "GoodBroker",
        "sector": "Logistics",
        "exposure_limit": 1000000.0,
        "debtor_days": 60.0,
        "financials_attached": True,
        "years_trading": 5.0,
        "broker_hit_rate": 0.8,  # Good broker
        "requested_cov_pct": 0.8,
        "has_judgements": False
    }
    
    poor_broker = good_broker.copy()
    poor_broker["submission_id"] = "poor_broker_001"
    poor_broker["broker_hit_rate"] = 0.3  # Poor broker
    
    # Test good broker
    response1 = client.post(
        "/triage/underwriting",
        json={"submissions": [good_broker]}
    )
    assert response1.status_code == 200
    score_good_broker = response1.json()[0]["score"]
    
    # Test poor broker
    response2 = client.post(
        "/triage/underwriting",
        json={"submissions": [poor_broker]}
    )
    assert response2.status_code == 200
    score_poor_broker = response2.json()[0]["score"]
    
    # Score with good broker should be higher
    assert score_good_broker > score_poor_broker


def test_batch_triage():
    """Test triaging multiple submissions in a single request."""
    submissions = [
        {
            "submission_id": "batch_001",
            "broker": "Broker1",
            "sector": "Retail",
            "exposure_limit": 2000000.0,
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
            "sector": "Services",
            "exposure_limit": 500000.0,
            "debtor_days": 120.0,
            "financials_attached": False,
            "years_trading": 2.0,
            "broker_hit_rate": 0.4,
            "requested_cov_pct": 0.9,
            "has_judgements": True
        }
    ]
    
    response = client.post(
        "/triage/underwriting",
        json={"submissions": submissions}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # First submission should have higher score (strong profile)
    # Second submission should have lower score (weak profile)
    assert data[0]["score"] > data[1]["score"]
    assert data[0]["id"] == "batch_001"
    assert data[1]["id"] == "batch_002"


def test_score_normalization():
    """Test that scores are properly normalized to 0-1 range."""
    submission = {
        "submission_id": "normalization_001",
        "broker": "TestBroker",
        "sector": "Other",
        "exposure_limit": 1000000.0,
        "debtor_days": 60.0,
        "financials_attached": True,
        "years_trading": 5.0,
        "broker_hit_rate": 0.6,
        "requested_cov_pct": 0.8,
        "has_judgements": False
    }
    
    response = client.post(
        "/triage/underwriting",
        json={"submissions": [submission]}
    )
    
    assert response.status_code == 200
    score = response.json()[0]["score"]
    
    # Score should be between 0 and 1
    assert 0 <= score <= 1
