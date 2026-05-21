import os
from typing import Dict, Optional
from src.resume_parser import ResumeParser
from src.skill_extractor import SkillExtractor
from src.job_matcher import JobMatcher
from src.components.model_trainer import ModelTrainer
from src.logger import logger
from src.exception import ResumeScreenerException

class PredictionPipeline:
    def __init__(self, top_k: int = 5):
        self.top_k = top_k
        self.parser = ResumeParser()
        self.skill_extractor = SkillExtractor()
        self.matcher: Optional[JobMatcher] = None
        self._load_or_train()

    def _load_or_train(self) -> None:
        try:
            self.matcher = ModelTrainer.load_matcher()
            logger.info("Pre-trained matcher loaded.")
        except ResumeScreenerException:
            logger.warning("No pre-trained model found. Running training pipeline...")
            from src.pipeline.training_pipeline import TrainingPipeline
            TrainingPipeline().run()
            self.matcher = ModelTrainer.load_matcher()

    def reload_jobs(self) -> None:
        self.matcher = ModelTrainer.load_matcher()
        logger.info("Matcher reloaded.")

    def predict_from_bytes(self, file_bytes: bytes, filename: str) -> Dict:
        parsed_resume = self.parser.parse_from_bytes(file_bytes, filename)
        resume_text = parsed_resume.raw_text
        if not resume_text.strip():
            raise ResumeScreenerException("Could not extract text from uploaded file.")
        logger.info(f"Resume text length: {len(resume_text)} chars")
        resume_skills = self.skill_extractor.extract_skills(resume_text)
        top_matches = self.matcher.match(resume_text, top_k=self.top_k)
        return {
            "resume_skills": resume_skills,
            "top_matches": top_matches,
            "resume_text_length": len(resume_text),
        }

    def predict_from_text(self, text: str) -> Dict:
        resume_skills = self.skill_extractor.extract_skills(text)
        top_matches = self.matcher.match(text, top_k=self.top_k)
        return {
            "resume_skills": resume_skills,
            "top_matches": top_matches,
            "resume_text_length": len(text),
        }