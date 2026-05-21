from src.job_matcher import JobMatcher
from src.logger import logger
from src.utils.common import save_json
import os
from typing import Dict, List, Optional

REPORT_PATH = "artifacts/reports/training_report.json"

class ModelEvaluator:
    def __init__(self, k_values=None):
        self.k_values = k_values or [1, 3, 5]

    def evaluate(self, matcher, test_samples=None, report_path=REPORT_PATH):
        if test_samples:
            metrics = self._compute_metrics(matcher, test_samples)
        else:
            metrics = self._placeholder_metrics(matcher)
        report = {"k_values": self.k_values, "metrics": metrics, "num_jobs": len(matcher._jobs), "status": "evaluated"}
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        save_json(report, report_path)
        return report

    def _compute_metrics(self, matcher, samples):
        results = {}
        for k in self.k_values:
            hits = 0
            precision_sum = 0.0
            for sample in samples:
                relevant = set(sample["relevant_ids"])
                top = matcher.match(sample["resume_text"], top_k=k)
                retrieved = {r["job_id"] for r in top}
                tp = len(relevant & retrieved)
                if tp > 0: hits += 1
                precision_sum += tp / k
            n = len(samples)
            results[f"precision_at_{k}"] = round(precision_sum / n, 4)
            results[f"hit_rate_at_{k}"] = round(hits / n, 4)
        return results

    def _placeholder_metrics(self, matcher):
        try:
            top = matcher.match("python machine learning sql", top_k=5)
            coverage = len(top)
        except Exception:
            coverage = 0
        return {"top_k_coverage": coverage, "note": "No labelled test data provided."}
