"""Tests for system endpoints."""

from fastapi.testclient import TestClient

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_status():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_version_reports_weights_version():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["weights_version"]


def test_reload_weights_endpoint():
    response = client.post("/admin/reload-weights")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "reloaded"
    assert data["weights_version"]


def test_config_current_includes_broker_curves():
    response = client.get("/config/current")
    assert response.status_code == 200
    data = response.json()
    assert "broker_score_curves" in data
    assert "sector_coverage_limits" in data
    assert "tier_1" in data["broker_score_curves"]
