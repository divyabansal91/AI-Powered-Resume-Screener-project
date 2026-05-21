from typing import Dict, List, Optional
from src.skill_extractor import SkillExtractor
from src.logger import logger
from src.exception import ResumeScreenerException

class JobMatcher:
    def __init__(self, similarity_weight=0.4, skill_weight=0.6, top_k=5):
        self.similarity_weight = similarity_weight
        self.skill_weight = skill_weight
        self.top_k = top_k
        self.skill_extractor = SkillExtractor()
        self._vectorizer = None
        self._job_vectors = None
        self._jobs = []

    def fit(self, jobs: List[Dict]) -> None:
        from sklearn.feature_extraction.text import TfidfVectorizer
        self._jobs = jobs
        corpus = [j.get("description", "") for j in jobs]
        self._vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1,2), sublinear_tf=True, stop_words="english")
        self._job_vectors = self._vectorizer.fit_transform(corpus)
        logger.info(f"JobMatcher fitted on {len(jobs)} jobs.")

    def match(self, resume_text: str, top_k: Optional[int] = None) -> List[Dict]:
        if self._vectorizer is None:
            raise ResumeScreenerException("JobMatcher not fitted. Call fit() first.")
        k = top_k or self.top_k
        from sklearn.metrics.pairwise import cosine_similarity
        resume_vec = self._vectorizer.transform([resume_text])
        cos_scores = cosine_similarity(resume_vec, self._job_vectors)[0]
        results = []
        for idx, job in enumerate(self._jobs):
            cos_sim = float(cos_scores[idx])
            skill_info = self.skill_extractor.skill_overlap(resume_text, job.get("description", ""))
            skill_ratio = skill_info["skill_match_ratio"]
            final_score = self.similarity_weight * cos_sim + self.skill_weight * skill_ratio
            results.append({
                "job_id": job.get("id", idx),
                "title": job.get("title", "Unknown"),
                "company": job.get("company", ""),
                "location": job.get("location", ""),
                "score": round(final_score, 4),
                "cosine_similarity": round(cos_sim, 4),
                "skill_match_ratio": round(skill_ratio, 4),
                "matched_skills": skill_info["matched_skills"],
                "missing_skills": skill_info["missing_skills"],
                "description_snippet": job.get("description", "")[:300],
            })
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:k]
