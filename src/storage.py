import json
import os
from datetime import datetime
from typing import Dict, Any

class SimpleStorage:
    def __init__(self, storage_dir: str = "data/requests"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_request_response(self, job_id: str, request_data: Dict[Any, Any], response_data: Dict[Any, Any]):
        """Save request and response for auditing"""
        record = {
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "request": request_data,
            "response": response_data
        }
        
        filepath = os.path.join(self.storage_dir, f"{job_id}.json")
        with open(filepath, 'w') as f:
            json.dump(record, f, indent=2)
    
    def get_record(self, job_id: str) -> Dict[Any, Any]:
        """Retrieve stored record"""
        filepath = os.path.join(self.storage_dir, f"{job_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return {}