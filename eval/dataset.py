import json
import os
from typing import List, Dict, Any

class TestDataset:
    def __init__(self, data_path: str = "data/test_cases.json"):
        self.data_path = data_path
        self.test_cases = self._load_test_cases()
    
    def _load_test_cases(self) -> List[Dict[str, Any]]:
        """Load test cases from JSON file"""
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as f:
                return json.load(f)
        return []
    
    def get_test_cases(self) -> List[Dict[str, Any]]:
        """Get all test cases"""
        return self.test_cases
    
    def get_noisy_cases(self) -> List[Dict[str, Any]]:
        """Get edge/noisy test cases"""
        return [case for case in self.test_cases if case.get("is_noisy", False)]