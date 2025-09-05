import pytest
import json
from fastapi.testclient import TestClient
from src.api import app
from src.config import API_KEY

client = TestClient(app)

@pytest.fixture
def test_case_data():
    """Load test case data from JSON file"""
    with open("data/test_cases.json", "r") as f:
        return json.load(f)[0]  # Use first test case

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "error-detection-api"

def test_detect_error_missing_auth(test_case_data):
    """Test detect-error endpoint without API key"""
    payload = {
        "question_url": test_case_data["question_url"],
        "solution_url": test_case_data["solution_url"],
        "bounding_box": test_case_data["bounding_box"]
    }
    
    response = client.post("/detect-error", json=payload)
    assert response.status_code == 401

def test_detect_error_invalid_payload():
    """Test detect-error endpoint with invalid payload"""
    payload = {
        "question_url": "invalid-url",
        # Missing required fields
    }
    
    headers = {"x-api-key": API_KEY}
    response = client.post("/detect-error", json=payload, headers=headers)
    assert response.status_code == 422  # Validation error

def test_detect_error_valid_auth(test_case_data):
    """Test detect-error endpoint with valid auth using real test data"""
    payload = {
        "question_url": test_case_data["question_url"],
        "solution_url": test_case_data["solution_url"],
        "bounding_box": test_case_data["bounding_box"],
        "question_id": test_case_data["question_id"]
    }
    
    headers = {"x-api-key": API_KEY}
    # This will likely fail due to OpenAI API call, but should pass auth
    response = client.post("/detect-error", json=payload, headers=headers)
    # Should not be 401 (auth error) or 422 (validation error)
    assert response.status_code not in [401, 422]