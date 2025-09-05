import pytest
import json
from src.models import DetectErrorRequest, DetectErrorResponse, BoundingBox

@pytest.fixture
def test_case_data():
    """Load test case data from JSON file"""
    with open("data/test_cases.json", "r") as f:
        return json.load(f)[0]

def test_bounding_box_creation():
    """Test BoundingBox model creation"""
    bbox = BoundingBox(minX=100, maxX=300, minY=50, maxY=100)
    assert bbox.minX == 100
    assert bbox.maxX == 300
    assert bbox.minY == 50
    assert bbox.maxY == 100

def test_detect_error_request(test_case_data):
    """Test DetectErrorRequest model validation with real data"""
    bbox = BoundingBox(**test_case_data["bounding_box"])
    request = DetectErrorRequest(
        question_url=test_case_data["question_url"],
        solution_url=test_case_data["solution_url"],
        bounding_box=bbox,
        question_id=test_case_data["question_id"]
    )
    assert request.question_url == test_case_data["question_url"]
    assert request.solution_url == test_case_data["solution_url"]
    assert request.question_id == test_case_data["question_id"]

def test_detect_error_response():
    """Test DetectErrorResponse model creation"""
    response = DetectErrorResponse(
        job_id="test-job-123",
        y=75.0,
        error="Test error",
        correction="Test correction",
        hint="Test hint",
        solution_complete=True,
        contains_diagram=False,
        question_has_diagram=False,
        solution_has_diagram=False,
        llm_used=True
    )
    assert response.job_id == "test-job-123"
    assert response.y == 75.0
    assert response.error == "Test error"
    assert response.llm_used is True