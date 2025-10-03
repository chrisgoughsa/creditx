"""Tests for health and version endpoints."""

import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "CreditX API"
    assert data["version"] == "1.0.0"


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["message"] == "CreditX API is running"
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_version_endpoint():
    """Test the version endpoint."""
    response = client.get("/version")
    
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["api_name"] == "CreditX API"
    assert "description" in data
    assert data["description"] == "Credit risk assessment and pricing system for insurance submissions and renewals"
    assert "build_date" in data
    assert data["weights_version"] == "1.0.0"


def test_health_endpoint_structure():
    """Test that health endpoint has the expected structure for monitoring."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    
    # Required fields for monitoring systems
    required_fields = ["status", "message", "version", "timestamp"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Status should be a string
    assert isinstance(data["status"], str)
    assert data["status"] == "healthy"


def test_version_endpoint_structure():
    """Test that version endpoint has the expected structure."""
    response = client.get("/version")
    
    assert response.status_code == 200
    data = response.json()
    
    # Required fields for version information
    required_fields = ["version", "api_name", "description", "build_date", "weights_version"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Version should be a string in semantic version format
    assert isinstance(data["version"], str)
    assert "." in data["version"]  # Basic check for semantic versioning


def test_endpoints_are_fast():
    """Test that health and version endpoints respond quickly."""
    import time
    
    # Test health endpoint speed
    start_time = time.time()
    response = client.get("/health")
    health_time = time.time() - start_time
    
    assert response.status_code == 200
    assert health_time < 0.1  # Should respond in under 100ms
    
    # Test version endpoint speed
    start_time = time.time()
    response = client.get("/version")
    version_time = time.time() - start_time
    
    assert response.status_code == 200
    assert version_time < 0.1  # Should respond in under 100ms


def test_health_endpoint_consistency():
    """Test that health endpoint returns consistent responses."""
    # Make multiple requests to ensure consistency
    responses = []
    for _ in range(5):
        response = client.get("/health")
        assert response.status_code == 200
        responses.append(response.json())
    
    # All responses should have the same structure
    first_response = responses[0]
    for response in responses[1:]:
        assert response["status"] == first_response["status"]
        assert response["message"] == first_response["message"]
        assert response["version"] == first_response["version"]


def test_version_endpoint_consistency():
    """Test that version endpoint returns consistent responses."""
    # Make multiple requests to ensure consistency
    responses = []
    for _ in range(5):
        response = client.get("/version")
        assert response.status_code == 200
        responses.append(response.json())
    
    # All responses should have the same structure
    first_response = responses[0]
    for response in responses[1:]:
        assert response["version"] == first_response["version"]
        assert response["api_name"] == first_response["api_name"]
        assert response["description"] == first_response["description"]
        assert response["build_date"] == first_response["build_date"]
        assert response["weights_version"] == first_response["weights_version"]
