import os
import pickle
from typing import Dict, List
from src.job_matcher import JobMatcher
from src.logger import logger
from src.exception import ResumeScreenerException
from src.utils.common import save_json

MODEL_DIR = "models/job_matcher"
MATCHER_PATH = os.path.join(MODEL_DIR, "job_matcher.pkl")
JOBS_PATH = os.path.join(MODEL_DIR, "jobs.json")

class ModelTrainer:
    def __init__(self):
        os.makedirs(MODEL_DIR, exist_ok=True)

    def train(self, jobs: List[Dict]) -> Dict:
        logger.info("Training JobMatcher...")
        matcher = JobMatcher(similarity_weight=0.4, skill_weight=0.6, top_k=5)
        matcher.fit(jobs)
        with open(MATCHER_PATH, "wb") as f:
            pickle.dump(matcher, f)
        logger.info(f"Model saved -> {MATCHER_PATH}")
        save_json(jobs, JOBS_PATH)
        return {"status": "success", "jobs_trained_on": len(jobs), "model_path": MATCHER_PATH}

    @staticmethod
    def load_matcher(path: str = MATCHER_PATH) -> JobMatcher:
        if not os.path.exists(path):
            raise ResumeScreenerException(f"Model not found at {path}. Run training first.")
        with open(path, "rb") as f:
            matcher = pickle.load(f)
        logger.info(f"Matcher loaded <- {path}")
        return matcher
