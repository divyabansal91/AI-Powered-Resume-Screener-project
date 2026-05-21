import sys
import numpy as np
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from src.logger import logger
from src.exception import ResumeScreenerException
from src.utils.common import save_object, load_object


class FeatureEngineer:
    """
    Build TF-IDF feature matrices for resume-job matching.
    Optionally supports sentence-transformer embeddings.
    """

    def __init__(
        self,
        max_features: int = 5000,
        ngram_range: Tuple[int, int] = (1, 2),
        vectorizer_path: str = "models/resume_parser/tfidf_vectorizer.pkl",
    ):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.vectorizer_path = vectorizer_path
        self._vectorizer = None
        logger.info(f"FeatureEngineer initialized — max_features={max_features}")

    def _get_vectorizer(self):
        """Lazy-init TF-IDF vectorizer."""
        if self._vectorizer is None:
            from sklearn.feature_extraction.text import TfidfVectorizer
            self._vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                stop_words='english',
                ngram_range=self.ngram_range,
                sublinear_tf=True,  # Apply log normalization
            )
        return self._vectorizer

    def fit_transform(self, texts: List[str]) -> np.ndarray:
        """Fit vectorizer on corpus and transform."""
        try:
            vectorizer = self._get_vectorizer()
            matrix = vectorizer.fit_transform(texts)
            logger.info(f"TF-IDF fitted — shape: {matrix.shape}")
            return matrix
        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def transform(self, texts: List[str]) -> np.ndarray:
        """Transform texts using already-fitted vectorizer."""
        try:
            if self._vectorizer is None:
                raise ValueError("Vectorizer not fitted yet. Call fit_transform first.")
            return self._vectorizer.transform(texts)
        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def save_vectorizer(self, path: Optional[str] = None):
        """Save fitted vectorizer to disk."""
        try:
            save_path = path or self.vectorizer_path
            save_object(save_path, self._vectorizer)
            logger.info(f"Vectorizer saved to {save_path}")
        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def load_vectorizer(self, path: Optional[str] = None):
        """Load vectorizer from disk."""
        try:
            load_path = path or self.vectorizer_path
            self._vectorizer = load_object(load_path)
            logger.info(f"Vectorizer loaded from {load_path}")
        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def compute_cosine_similarity_matrix(self, matrix_a, matrix_b) -> np.ndarray:
        """Compute cosine similarity between two TF-IDF matrices."""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            sim = cosine_similarity(matrix_a, matrix_b)
            return sim
        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def build_skill_feature_vector(
        self, skills: List[str], all_skills: List[str]
    ) -> np.ndarray:
        """
        Binary feature vector: 1 if skill present, 0 otherwise.
        Used for skill-based similarity.
        """
        skill_set = set(s.lower() for s in skills)
        vector = np.array([1.0 if s.lower() in skill_set else 0.0 for s in all_skills])
        return vector

    def get_feature_names(self) -> List[str]:
        """Return feature names from fitted vectorizer."""
        if self._vectorizer is None:
            return []
        return self._vectorizer.get_feature_names_out().tolist()