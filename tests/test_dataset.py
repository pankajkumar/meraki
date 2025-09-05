import pytest
import json
import tempfile
import os
from eval.dataset import TestDataset

@pytest.fixture
def sample_test_data():
    """Load real test data from test_cases.json"""
    with open("data/test_cases.json", "r") as f:
        data = json.load(f)
    # Add is_noisy field to first two cases for testing
    data[0]["is_noisy"] = False
    data[1]["is_noisy"] = True
    return data[:2]

def test_dataset_load_existing_file():
    """Test loading real test dataset"""
    dataset = TestDataset("data/test_cases.json")
    test_cases = dataset.get_test_cases()
    
    assert len(test_cases) >= 4
    assert test_cases[0]["question_id"] == "question_1"
    assert "question_url" in test_cases[0]
    assert "solution_url" in test_cases[0]
    assert "has_error" in test_cases[0]

def test_dataset_load_nonexistent_file():
    """Test loading non-existent dataset file"""
    dataset = TestDataset("nonexistent.json")
    test_cases = dataset.get_test_cases()
    assert test_cases == []

def test_dataset_get_noisy_cases(sample_test_data):
    """Test filtering noisy test cases"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_test_data, f)
        temp_path = f.name
    
    try:
        dataset = TestDataset(temp_path)
        noisy_cases = dataset.get_noisy_cases()
        
        assert len(noisy_cases) == 1
        assert noisy_cases[0]["question_id"] == "question_2"
        assert noisy_cases[0]["is_noisy"] is True
    finally:
        os.unlink(temp_path)