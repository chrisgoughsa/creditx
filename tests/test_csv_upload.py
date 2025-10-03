"""Tests for CSV upload functionality."""

import io
import pytest
from fastapi.testclient import TestClient

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.main import app

client = TestClient(app)


@pytest.fixture
def valid_submissions_csv():
    """Valid submissions CSV content."""
    return """submission_id,broker,sector,exposure_limit,debtor_days,financials_attached,years_trading,broker_hit_rate,requested_cov_pct,has_judgements
sub001,PremiumBroker,Retail,1000000.0,45.0,true,8.0,0.85,0.75,false
sub002,NewBroker,Manufacturing,500000.0,120.0,false,1.5,0.3,0.95,true"""


@pytest.fixture
def valid_policies_csv():
    """Valid policies CSV content."""
    return """policy_id,sector,current_premium,limit,utilization_pct,claims_last_24m_cnt,claims_ratio_24m,days_to_expiry,requested_change_pct,broker
pol001,Retail,50000.0,1000000.0,0.8,2,0.5,30.0,-0.1,PremiumBroker
pol002,Services,25000.0,500000.0,0.3,0,0.0,180.0,0.05,NewBroker"""


def test_valid_submissions_csv_upload(valid_submissions_csv):
    """Test uploading valid submissions CSV."""
    csv_file = io.BytesIO(valid_submissions_csv.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("submissions.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Check that we get triage scores
    assert all("id" in item for item in data)
    assert all("score" in item for item in data)
    assert all("reasons" in item for item in data)
    assert all(0 <= item["score"] <= 1 for item in data)


def test_valid_policies_csv_upload(valid_policies_csv):
    """Test uploading valid policies CSV."""
    csv_file = io.BytesIO(valid_policies_csv.encode('utf-8'))
    
    response = client.post(
        "/renewals/priority/csv",
        files={"file": ("policies.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    
    # Check that we get priority scores
    assert all("id" in item for item in data)
    assert all("score" in item for item in data)
    assert all("reasons" in item for item in data)
    assert all(0 <= item["score"] <= 1 for item in data)


def test_missing_required_columns_submissions():
    """Test CSV with missing required columns for submissions."""
    invalid_csv = """submission_id,broker,sector,exposure_limit,debtor_days
sub001,PremiumBroker,Retail,1000000.0,45.0"""
    
    csv_file = io.BytesIO(invalid_csv.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("submissions.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Missing required columns" in data["detail"]
    assert "financials_attached" in data["detail"]
    assert "years_trading" in data["detail"]


def test_missing_required_columns_policies():
    """Test CSV with missing required columns for policies."""
    invalid_csv = """policy_id,sector,current_premium,limit
pol001,Retail,50000.0,1000000.0"""
    
    csv_file = io.BytesIO(invalid_csv.encode('utf-8'))
    
    response = client.post(
        "/renewals/priority/csv",
        files={"file": ("policies.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Missing required columns" in data["detail"]
    assert "utilization_pct" in data["detail"]
    assert "claims_last_24m_cnt" in data["detail"]


def test_empty_csv():
    """Test uploading empty CSV file."""
    empty_csv = ""
    csv_file = io.BytesIO(empty_csv.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("empty.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "CSV file is empty" in data["detail"]


def test_csv_with_only_headers():
    """Test CSV with only headers and no data rows."""
    headers_only = """submission_id,broker,sector,exposure_limit,debtor_days,financials_attached,years_trading,broker_hit_rate,requested_cov_pct,has_judgements"""
    
    csv_file = io.BytesIO(headers_only.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("headers_only.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "CSV file is empty" in data["detail"]


def test_invalid_file_extension():
    """Test uploading non-CSV file."""
    text_content = "This is not a CSV file"
    text_file = io.BytesIO(text_content.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("data.txt", text_file, "text/plain")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "File must be a CSV file" in data["detail"]


def test_invalid_data_types_submissions():
    """Test CSV with invalid data types for submissions."""
    invalid_csv = """submission_id,broker,sector,exposure_limit,debtor_days,financials_attached,years_trading,broker_hit_rate,requested_cov_pct,has_judgements
sub001,PremiumBroker,Retail,not_a_number,45.0,true,8.0,0.85,0.75,false"""
    
    csv_file = io.BytesIO(invalid_csv.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("invalid.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Error parsing row 1" in data["detail"]


def test_invalid_data_types_policies():
    """Test CSV with invalid data types for policies."""
    invalid_csv = """policy_id,sector,current_premium,limit,utilization_pct,claims_last_24m_cnt,claims_ratio_24m,days_to_expiry,requested_change_pct,broker
pol001,Retail,not_a_number,1000000.0,0.8,2,0.5,30.0,-0.1,PremiumBroker"""
    
    csv_file = io.BytesIO(invalid_csv.encode('utf-8'))
    
    response = client.post(
        "/renewals/priority/csv",
        files={"file": ("invalid.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Error parsing row 1" in data["detail"]


def test_boolean_field_parsing():
    """Test various boolean field formats."""
    csv_content = """submission_id,broker,sector,exposure_limit,debtor_days,financials_attached,years_trading,broker_hit_rate,requested_cov_pct,has_judgements
sub001,PremiumBroker,Retail,1000000.0,45.0,1,8.0,0.85,0.75,0
sub002,NewBroker,Manufacturing,500000.0,120.0,yes,1.5,0.3,0.95,y
sub003,TestBroker,Services,750000.0,60.0,no,5.0,0.6,0.8,n"""
    
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("boolean_test.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_unicode_encoding_error():
    """Test CSV with invalid encoding."""
    # Create bytes that are not valid UTF-8
    invalid_utf8 = b'\xff\xfe\x00\x00'  # Invalid UTF-8 sequence
    csv_file = io.BytesIO(invalid_utf8)
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("invalid_encoding.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "CSV file must be UTF-8 encoded" in data["detail"]


def test_large_csv_file():
    """Test uploading a larger CSV file with multiple rows."""
    # Generate a CSV with 100 rows
    csv_lines = ["submission_id,broker,sector,exposure_limit,debtor_days,financials_attached,years_trading,broker_hit_rate,requested_cov_pct,has_judgements"]
    
    for i in range(100):
        csv_lines.append(f"sub{i:03d},Broker{i%5},Retail,{1000000 + i*10000},45.0,true,8.0,0.85,0.75,false")
    
    large_csv = "\n".join(csv_lines)
    csv_file = io.BytesIO(large_csv.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("large.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 100


def test_mixed_case_boolean_values():
    """Test boolean fields with mixed case values."""
    csv_content = """submission_id,broker,sector,exposure_limit,debtor_days,financials_attached,years_trading,broker_hit_rate,requested_cov_pct,has_judgements
sub001,PremiumBroker,Retail,1000000.0,45.0,TRUE,8.0,0.85,0.75,FALSE
sub002,NewBroker,Manufacturing,500000.0,120.0,True,1.5,0.3,0.95,False
sub003,TestBroker,Services,750000.0,60.0,Yes,5.0,0.6,0.8,No"""
    
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("mixed_case.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_extra_columns_ignored():
    """Test CSV with extra columns that should be ignored."""
    csv_content = """submission_id,broker,sector,exposure_limit,debtor_days,financials_attached,years_trading,broker_hit_rate,requested_cov_pct,has_judgements,extra_column1,extra_column2
sub001,PremiumBroker,Retail,1000000.0,45.0,true,8.0,0.85,0.75,false,ignored1,ignored2"""
    
    csv_file = io.BytesIO(csv_content.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("extra_columns.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


def test_malformed_csv():
    """Test CSV with malformed structure."""
    malformed_csv = """submission_id,broker,sector,exposure_limit,debtor_days,financials_attached,years_trading,broker_hit_rate,requested_cov_pct,has_judgements
sub001,PremiumBroker,Retail,1000000.0,45.0,true,8.0,0.85,0.75,false
sub002,NewBroker,Manufacturing,500000.0,120.0,false,1.5,0.3,0.95,true
sub003,TestBroker,Services,750000.0,60.0,true,5.0,0.6,0.8,false
sub004,IncompleteBroker,Logistics,800000.0,90.0,true,3.0,0.7,0.85"""  # Missing last column
    
    csv_file = io.BytesIO(malformed_csv.encode('utf-8'))
    
    response = client.post(
        "/triage/underwriting/csv",
        files={"file": ("malformed.csv", csv_file, "text/csv")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "Error parsing row 4" in data["detail"]
