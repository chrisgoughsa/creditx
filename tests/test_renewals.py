"""Tests for renewal priority functionality."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).parent.parent))

from app.main import app  # noqa: E402

client = TestClient(app)


def test_renewal_priority_endpoint():
    """Test renewal priority scoring for a single policy."""
    policy = {
        "policy_id": "renewal_001",
        "sector": "Retail",
        "current_premium": 75000.0,
        "limit": 2500000.0,
        "utilization_pct": 0.85,
        "claims_last_24m_cnt": 3,
        "claims_ratio_24m": 0.2,
        "days_to_expiry": 20.0,
        "requested_change_pct": -0.15,
        "broker": "PremiumBroker",
    }

    response = client.post("/renewals/priority", json={"policies": [policy]})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["scores"]) == 1
    result = payload["scores"][0]
    assert isinstance(payload["feature_importance"], dict)
    assert result["id"] == "renewal_001"
    assert 0 <= result["score"] <= 1
    assert "Expiring within 30 days" in result["reasons"]
    assert "High utilization" in result["reasons"]


def test_renewals_csv_upload_round_trip():
    """Test that CSV upload returns renewal priority scores."""
    csv_bytes = Path("sample_data/renewals.csv").read_bytes()
    response = client.post(
        "/renewals/priority/csv",
        files={"file": ("renewals.csv", csv_bytes, "text/csv")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["scores"]) > 0
    assert {record["id"] for record in payload["scores"]}
    assert isinstance(payload["feature_importance"], dict)


def test_renewals_csv_missing_required_column():
    """Ensure missing column errors are surfaced clearly."""
    csv_content = "policy_id,broker\nPOL-404,MissingBroker"
    response = client.post(
        "/renewals/priority/csv",
        files={"file": ("broken.csv", csv_content, "text/csv")},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert "Missing required columns" in detail


def test_policy_check_allows_within_limit():
    """Policy check should allow coverage within configured limits."""
    response = client.post(
        "/policy/check",
        json={"sector": "Retail", "requested_cov_pct": 0.85},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["allowed"] is True
    assert payload["max_allowed_cov_pct"] >= 0.85


def test_policy_check_rejects_exceeding_limit():
    """Policy check should reject coverage above sector threshold."""
    response = client.post(
        "/policy/check",
        json={"sector": "Services", "requested_cov_pct": 0.95},
    )

    assert response.status_code == 400
    assert "exceeds limit" in response.json()["detail"]
