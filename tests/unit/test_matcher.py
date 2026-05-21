import pytest
from src.skill_extractor import SkillExtractor
from src.job_matcher import JobMatcher, JobMatch


SAMPLE_JOBS = [
    {
        "job_id": "J001",
        "title": "ML Engineer",
        "company": "TechCorp",
        "location": "Bangalore",
        "description": "We need Python, TensorFlow, Docker, AWS skills.",
        "required_skills": ["python", "tensorflow", "docker", "aws"],
    },
    {
        "job_id": "J002",
        "title": "Data Scientist",
        "company": "DataCo",
        "location": "Mumbai",
        "description": "Looking for Python, pandas, scikit-learn, SQL expert.",
        "required_skills": ["python", "pandas", "scikit-learn", "sql"],
    },
]


class TestSkillExtractor:

    def setup_method(self):
        self.extractor = SkillExtractor()

    def test_extract_known_skill(self):
        text = "I have experience with Python and TensorFlow"
        skills = self.extractor.extract(text)
        assert "python" in skills
        assert "tensorflow" in skills

    def test_extract_returns_list(self):
        skills = self.extractor.extract("Python developer")
        assert isinstance(skills, list)

    def test_extract_with_categories(self):
        text = "Python, React, MySQL, Docker"
        result = self.extractor.extract_with_categories(text)
        assert isinstance(result, dict)
        assert any("python" in v for v in result.values())

    def test_skill_match_score_perfect(self):
        resume_skills = ["python", "docker", "aws"]
        job_skills = ["python", "docker", "aws"]
        score = self.extractor.skill_match_score(resume_skills, job_skills)
        assert score == 1.0

    def test_skill_match_score_partial(self):
        resume_skills = ["python", "docker"]
        job_skills = ["python", "docker", "aws", "kubernetes"]
        score = self.extractor.skill_match_score(resume_skills, job_skills)
        assert 0.0 < score < 1.0

    def test_skill_match_score_zero(self):
        score = self.extractor.skill_match_score([], ["python", "java"])
        assert score == 0.0

    def test_get_missing_skills(self):
        resume_skills = ["python"]
        job_skills = ["python", "docker", "aws"]
        missing = self.extractor.get_missing_skills(resume_skills, job_skills)
        assert "docker" in missing
        assert "aws" in missing
        assert "python" not in missing

    def test_skill_gap_report_structure(self):
        report = self.extractor.get_skill_gap_report(["python"], ["python", "docker"])
        assert "score" in report
        assert "matched_skills" in report
        assert "missing_skills" in report
        assert "percentage" in report


class TestJobMatcher:

    def setup_method(self):
        self.matcher = JobMatcher()

    def test_match_returns_list(self):
        results = self.matcher.match(
            resume_text="python machine learning tensorflow",
            resume_skills=["python", "tensorflow"],
            job_listings=SAMPLE_JOBS,
            top_k=2,
        )
        assert isinstance(results, list)
        assert len(results) <= 2

    def test_match_sorted_by_score(self):
        results = self.matcher.match(
            resume_text="python machine learning tensorflow docker aws",
            resume_skills=["python", "tensorflow", "docker", "aws"],
            job_listings=SAMPLE_JOBS,
            top_k=2,
        )
        if len(results) >= 2:
            assert results[0].final_score >= results[1].final_score

    def test_match_returns_job_match_objects(self):
        results = self.matcher.match("python", ["python"], SAMPLE_JOBS, top_k=1)
        assert isinstance(results[0], JobMatch)

    def test_recommend_skills(self):
        rec = self.matcher.recommend_skills(
            resume_skills=["python"],
            target_job_skills=["python", "docker", "aws"],
        )
        assert "skills_to_learn" in rec
        assert "current_score" in rec
        assert "docker" in rec["skills_to_learn"] or "aws" in rec["skills_to_learn"]