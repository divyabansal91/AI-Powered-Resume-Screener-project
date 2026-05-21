import sys
import re
from typing import List, Dict, Any
from pathlib import Path

from src.logger import logger
from src.exception import ResumeScreenerException
from src.utils.text_processing import clean_text, remove_stopwords, tokenize


class DataPreprocessor:
    """
    Preprocess both resume text and job descriptions
    for consistent NLP processing.
    """

    def __init__(self):
        logger.info("DataPreprocessor initialized")

    def preprocess_resume(self, parsed_resume: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize parsed resume data."""
        try:
            processed = dict(parsed_resume)
            processed["clean_text"] = clean_text(parsed_resume.get("raw_text", ""))
            processed["tokens"] = remove_stopwords(tokenize(processed["clean_text"]))

            # Normalize skills to lowercase
            processed["skills"] = [
                s.lower().strip() for s in parsed_resume.get("skills", [])
            ]

            logger.info("Resume preprocessed successfully")
            return processed
        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def preprocess_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize job listing data."""
        try:
            processed = dict(job)
            raw_desc = job.get("description", "")
            processed["clean_description"] = clean_text(raw_desc)
            processed["tokens"] = remove_stopwords(tokenize(processed["clean_description"]))

            # Normalize required_skills
            processed["required_skills"] = [
                s.lower().strip() for s in job.get("required_skills", [])
            ]

            logger.info(f"Job preprocessed: {job.get('title', 'unknown')}")
            return processed
        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def preprocess_jobs_batch(self, jobs: List[Dict]) -> List[Dict]:
        """Preprocess a list of job listings."""
        try:
            processed = [self.preprocess_job(job) for job in jobs]
            logger.info(f"Batch preprocessed {len(processed)} jobs")
            return processed
        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def build_combined_text(self, resume_dict: Dict) -> str:
        """
        Combine key resume fields into a single text blob
        for TF-IDF vectorization.
        """
        parts = [
            resume_dict.get("clean_text", ""),
            " ".join(resume_dict.get("skills", [])),
            " ".join(resume_dict.get("education", [])),
        ]
        return " ".join(filter(None, parts))

    def normalize_skill_list(self, skills: List[str]) -> List[str]:
        """Lowercase + strip + deduplicate skills."""
        seen = set()
        result = []
        for s in skills:
            normalized = s.lower().strip()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(normalized)
        return result