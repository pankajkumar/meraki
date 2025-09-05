import pytest
import os
import tempfile
import shutil
from src.storage import SimpleStorage

@pytest.fixture
def temp_storage():
    """Create temporary storage for testing"""
    temp_dir = tempfile.mkdtemp()
    storage = SimpleStorage(temp_dir)
    yield storage
    shutil.rmtree(temp_dir)

def test_save_and_retrieve_record(temp_storage):
    """Test saving and retrieving records"""
    job_id = "test-job-123"
    request_data = {"test": "request"}
    response_data = {"test": "response"}
    
    # Save record
    temp_storage.save_request_response(job_id, request_data, response_data)
    
    # Retrieve record
    record = temp_storage.get_record(job_id)
    
    assert record["job_id"] == job_id
    assert record["request"] == request_data
    assert record["response"] == response_data
    assert "timestamp" in record

def test_get_nonexistent_record(temp_storage):
    """Test retrieving non-existent record"""
    record = temp_storage.get_record("nonexistent")
    assert record == {}

def test_storage_directory_creation():
    """Test that storage directory is created"""
    temp_dir = tempfile.mkdtemp()
    storage_path = os.path.join(temp_dir, "new_storage")
    
    # Directory shouldn't exist initially
    assert not os.path.exists(storage_path)
    
    # Creating storage should create directory
    storage = SimpleStorage(storage_path)
    assert os.path.exists(storage_path)
    
    # Cleanup
    shutil.rmtree(temp_dir)