import asyncio
import json
import time
import csv
from typing import Dict, Any, List
from src.detector import ErrorDetector
from src.detector_variants import BaselineDetector, ImprovedDetector
from src.models import DetectErrorRequest, BoundingBox
from eval.dataset import TestDataset
from eval.metrics import MetricsCalculator, AccuracyMetrics

class EvaluationHarness:
    def __init__(self):
        self.baseline_detector = BaselineDetector()
        self.improved_detector = ImprovedDetector()
        self.dataset = TestDataset()
        self.baseline_metrics = MetricsCalculator()
        self.improved_metrics = MetricsCalculator()
        self.baseline_accuracy = AccuracyMetrics()
        self.improved_accuracy = AccuracyMetrics()
        self.results = []
    
    async def run_evaluation(self):
        """Run complete evaluation pipeline"""
        print("Starting Error Detection API Evaluation...")
        print("=" * 50)
        
        test_cases = self.dataset.get_test_cases()
        print(f"Loaded {len(test_cases)} test cases")
        print(f"Noisy cases: {len(self.dataset.get_noisy_cases())}")
        
        # Run baseline evaluation
        print(f"\nRunning BASELINE evaluation...")
        baseline_results = await self._evaluate_variant("baseline", test_cases, self.baseline_detector, self.baseline_metrics, self.baseline_accuracy)
        
        # Run improved evaluation
        print(f"\nRunning IMPROVED evaluation...")
        improved_results = await self._evaluate_variant("improved", test_cases, self.improved_detector, self.improved_metrics, self.improved_accuracy)
        
        # Store results for export
        self.results = {
            "baseline": baseline_results,
            "improved": improved_results
        }
        
        # Print results
        self._print_results()
        
        # Export results
        self._export_results()
        
        # Robustness analysis
        self._analyze_robustness()
    
    async def _evaluate_variant(self, variant: str, test_cases: list, detector, metrics: MetricsCalculator, accuracy: AccuracyMetrics) -> List[Dict]:
        """Evaluate a specific variant"""
        variant_results = []
        
        for i, case in enumerate(test_cases):
            print(f"Processing {variant} case {i+1}/{len(test_cases)}: {case['question_id']}")
            
            start_time = time.time()
            success = True
            error = None
            response = None
            
            try:
                request = DetectErrorRequest(
                    question_url=case["question_url"],
                    solution_url=case["solution_url"],
                    bounding_box=BoundingBox(**case["bounding_box"]),
                    question_id=case.get("question_id", f"test_{i}")
                )
                
                response = await detector.detect_error(request)
                
                # Evaluate accuracy
                predicted_has_error = "no error" not in response.error.lower()
                actual_has_error = case["has_error"]
                accuracy.record_prediction(predicted_has_error, actual_has_error)
                
            except Exception as e:
                success = False
                error = str(e)
            
            latency = time.time() - start_time
            metrics.record_request(latency, success, error)
            
            # Store detailed results
            result = {
                "case_id": case["question_id"],
                "variant": variant,
                "latency": latency,
                "success": success,
                "error": error,
                "predicted_error": response.error if response else None,
                "actual_has_error": case["has_error"],
                "predicted_has_error": "no error" not in response.error.lower() if response else False,
                "is_noisy": case.get("is_noisy", False)
            }
            variant_results.append(result)
        
        return variant_results
    
    def _print_results(self):
        """Print evaluation results"""
        baseline_summary = self.baseline_metrics.get_summary()
        improved_summary = self.improved_metrics.get_summary()
        baseline_acc = self.baseline_accuracy.get_summary()
        improved_acc = self.improved_accuracy.get_summary()
        
        print("\n" + "=" * 70)
        print("EVALUATION RESULTS - ML QUALITY & METRICS")
        print("=" * 70)
        
        print(f"{'Metric':<25} {'Baseline':<20} {'Improved':<20} {'Δ Change':<15}")
        print("-" * 70)
        
        # Performance Metrics
        print(f"{'Success Rate':<25} {baseline_summary['success_rate']:<20.3f} {improved_summary['success_rate']:<20.3f} {improved_summary['success_rate']-baseline_summary['success_rate']:+.3f}")
        print(f"{'P50 Latency (s)':<25} {baseline_summary['latency_p50']:<20.3f} {improved_summary['latency_p50']:<20.3f} {improved_summary['latency_p50']-baseline_summary['latency_p50']:+.3f}")
        print(f"{'P90 Latency (s)':<25} {baseline_summary['latency_p90']:<20.3f} {improved_summary['latency_p90']:<20.3f} {improved_summary['latency_p90']-baseline_summary['latency_p90']:+.3f}")
        print(f"{'P95 Latency (s)':<25} {baseline_summary['latency_p95']:<20.3f} {improved_summary['latency_p95']:<20.3f} {improved_summary['latency_p95']-baseline_summary['latency_p95']:+.3f}")
        
        # ML Quality Metrics
        print(f"{'Accuracy':<25} {baseline_acc['accuracy']:<20.3f} {improved_acc['accuracy']:<20.3f} {improved_acc['accuracy']-baseline_acc['accuracy']:+.3f}")
        print(f"{'Precision':<25} {baseline_acc['precision']:<20.3f} {improved_acc['precision']:<20.3f} {improved_acc['precision']-baseline_acc['precision']:+.3f}")
        print(f"{'Recall':<25} {baseline_acc['recall']:<20.3f} {improved_acc['recall']:<20.3f} {improved_acc['recall']-baseline_acc['recall']:+.3f}")
        print(f"{'F1 Score':<25} {baseline_acc['f1_score']:<20.3f} {improved_acc['f1_score']:<20.3f} {improved_acc['f1_score']-baseline_acc['f1_score']:+.3f}")
        
        # Cost Analysis
        cost_per_100 = self._estimate_cost(baseline_summary['total_requests'])
        print(f"\nCost per 100 requests: ${cost_per_100:.2f}")
        print(f"Total test cases: {baseline_summary['total_requests']}")
        print(f"Noisy cases: {len(self.dataset.get_noisy_cases())}")
    
    def _estimate_cost(self, request_count: int) -> float:
        """Rough cost estimation"""
        # GPT-4o: ~$0.005 per image, GPT-4: ~$0.03 per 1K tokens
        cost_per_request = 0.01 + 0.02  # Vision + text analysis
        return (cost_per_request * 100)
    
    def _export_results(self):
        """Export results to JSON and CSV"""
        summary_results = {
            "baseline": {
                "performance": self.baseline_metrics.get_summary(),
                "accuracy": self.baseline_accuracy.get_summary()
            },
            "improved": {
                "performance": self.improved_metrics.get_summary(),
                "accuracy": self.improved_accuracy.get_summary()
            },
            "timestamp": time.time(),
            "test_cases_count": len(self.dataset.get_test_cases()),
            "noisy_cases_count": len(self.dataset.get_noisy_cases())
        }
        
        # Export summary
        with open("eval_results.json", 'w') as f:
            json.dump(summary_results, f, indent=2)
        
        # Export detailed per-case results
        all_results = self.results["baseline"] + self.results["improved"]
        with open("eval_detailed_results.csv", 'w', newline='') as f:
            if all_results:
                writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
                writer.writeheader()
                writer.writerows(all_results)
        
        print(f"\nResults exported to:")
        print(f"  - eval_results.json (summary)")
        print(f"  - eval_detailed_results.csv (per-case)")
    
    def _analyze_robustness(self):
        """Analyze performance on noisy/edge cases"""
        print("\n" + "=" * 50)
        print("ROBUSTNESS ANALYSIS")
        print("=" * 50)
        
        noisy_baseline = [r for r in self.results["baseline"] if r["is_noisy"]]
        noisy_improved = [r for r in self.results["improved"] if r["is_noisy"]]
        
        if noisy_baseline and noisy_improved:
            baseline_noisy_acc = sum(1 for r in noisy_baseline if r["predicted_has_error"] == r["actual_has_error"]) / len(noisy_baseline)
            improved_noisy_acc = sum(1 for r in noisy_improved if r["predicted_has_error"] == r["actual_has_error"]) / len(noisy_improved)
            
            print(f"Noisy cases accuracy:")
            print(f"  Baseline: {baseline_noisy_acc:.3f}")
            print(f"  Improved: {improved_noisy_acc:.3f}")
            print(f"  Delta: {improved_noisy_acc - baseline_noisy_acc:+.3f}")
        else:
            print("No noisy cases found for robustness analysis")

async def main():
    harness = EvaluationHarness()
    await harness.run_evaluation()

if __name__ == "__main__":
    asyncio.run(main())