import pytest
from eval.metrics import AccuracyMetrics, MetricsCalculator

def test_accuracy_metrics_empty():
    """Test AccuracyMetrics with no data"""
    metrics = AccuracyMetrics()
    summary = metrics.get_summary()
    assert summary["accuracy"] == 0
    assert summary["precision"] == 0
    assert summary["recall"] == 0
    assert summary["f1_score"] == 0

def test_accuracy_metrics_perfect():
    """Test AccuracyMetrics with perfect predictions"""
    metrics = AccuracyMetrics()
    # All correct predictions
    metrics.record_prediction(True, True)   # TP
    metrics.record_prediction(False, False) # TN
    metrics.record_prediction(True, True)   # TP
    metrics.record_prediction(False, False) # TN
    
    summary = metrics.get_summary()
    assert summary["accuracy"] == 1.0
    assert summary["precision"] == 1.0
    assert summary["recall"] == 1.0
    assert summary["f1_score"] == 1.0
    assert summary["true_positives"] == 2
    assert summary["true_negatives"] == 2

def test_accuracy_metrics_mixed():
    """Test AccuracyMetrics with mixed predictions"""
    metrics = AccuracyMetrics()
    metrics.record_prediction(True, True)    # TP
    metrics.record_prediction(True, False)   # FP
    metrics.record_prediction(False, True)   # FN
    metrics.record_prediction(False, False)  # TN
    
    summary = metrics.get_summary()
    assert summary["accuracy"] == 0.5  # (TP + TN) / Total = (1 + 1) / 4
    assert summary["precision"] == 0.5  # TP / (TP + FP) = 1 / (1 + 1)
    assert summary["recall"] == 0.5     # TP / (TP + FN) = 1 / (1 + 1)

def test_metrics_calculator():
    """Test MetricsCalculator for latency and success tracking"""
    calc = MetricsCalculator()
    
    # Record some requests
    calc.record_request(1.5, True)
    calc.record_request(2.0, True)
    calc.record_request(3.0, False, "timeout")
    calc.record_request(1.0, True)
    
    summary = calc.get_summary()
    assert summary["total_requests"] == 4
    assert summary["success_rate"] == 0.75  # 3/4
    assert summary["error_count"] == 1
    
    percentiles = calc.get_latency_percentiles()
    assert percentiles["p50"] > 0
    assert percentiles["p95"] > 0