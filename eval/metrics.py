import time
import statistics
from typing import List, Dict, Any

class AccuracyMetrics:
    def __init__(self):
        self.true_positives = 0
        self.false_positives = 0
        self.true_negatives = 0
        self.false_negatives = 0
    
    def record_prediction(self, predicted: bool, actual: bool):
        """Record a prediction for accuracy calculation"""
        if predicted and actual:
            self.true_positives += 1
        elif predicted and not actual:
            self.false_positives += 1
        elif not predicted and actual:
            self.false_negatives += 1
        else:
            self.true_negatives += 1
    
    def get_summary(self) -> Dict[str, float]:
        """Calculate accuracy metrics"""
        total = self.true_positives + self.false_positives + self.true_negatives + self.false_negatives
        
        if total == 0:
            return {"accuracy": 0, "precision": 0, "recall": 0, "f1_score": 0}
        
        accuracy = (self.true_positives + self.true_negatives) / total
        
        precision = self.true_positives / (self.true_positives + self.false_positives) if (self.true_positives + self.false_positives) > 0 else 0
        recall = self.true_positives / (self.true_positives + self.false_negatives) if (self.true_positives + self.false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "true_positives": self.true_positives,
            "false_positives": self.false_positives,
            "true_negatives": self.true_negatives,
            "false_negatives": self.false_negatives
        }

class MetricsCalculator:
    def __init__(self):
        self.latencies = []
        self.successes = 0
        self.total_requests = 0
        self.errors = []
    
    def record_request(self, latency: float, success: bool, error: str = None):
        """Record a request result"""
        self.latencies.append(latency)
        self.total_requests += 1
        if success:
            self.successes += 1
        else:
            self.errors.append(error or "Unknown error")
    
    def get_latency_percentiles(self) -> Dict[str, float]:
        """Calculate latency percentiles"""
        if not self.latencies:
            return {"p50": 0, "p90": 0, "p95": 0}
        
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        return {
            "p50": sorted_latencies[int(n * 0.5)],
            "p90": sorted_latencies[int(n * 0.9)],
            "p95": sorted_latencies[int(n * 0.95)]
        }
    
    def get_success_rate(self) -> float:
        """Calculate success rate"""
        if self.total_requests == 0:
            return 0.0
        return self.successes / self.total_requests
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete metrics summary"""
        percentiles = self.get_latency_percentiles()
        return {
            "total_requests": self.total_requests,
            "success_rate": self.get_success_rate(),
            "latency_p50": percentiles["p50"],
            "latency_p90": percentiles["p90"],
            "latency_p95": percentiles["p95"],
            "avg_latency": statistics.mean(self.latencies) if self.latencies else 0,
            "error_count": len(self.errors),
            "unique_errors": len(set(self.errors))
        }