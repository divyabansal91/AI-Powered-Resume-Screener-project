import sys
from typing import Dict
from src.components.data_ingestion import DataIngestion
from src.components.data_preprocessing import DataPreprocessor
from src.components.model_trainer import ModelTrainer
from src.components.model_evaluator import ModelEvaluator
from src.logger import logger
from src.exception import ResumeScreenerException

class TrainingPipeline:
    def run(self) -> Dict:
        try:
            logger.info("=" * 60)
            logger.info("TRAINING PIPELINE STARTED")
            logger.info("=" * 60)
            jobs_raw = DataIngestion().initiate_data_ingestion()
            jobs = DataPreprocessor().preprocess_jobs_batch(jobs_raw)
            trainer = ModelTrainer()
            train_report = trainer.train(jobs)
            matcher = ModelTrainer.load_matcher()
            eval_report = ModelEvaluator().evaluate(matcher)
            report = {**train_report, "evaluation": eval_report}
            logger.info("TRAINING PIPELINE COMPLETE")
            return report
        except Exception as e:
            raise ResumeScreenerException(e, sys)