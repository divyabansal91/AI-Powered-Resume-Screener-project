import pytest
from src.skill_extractor import SkillExtractor
from src.job_matcher import JobMatcher


SAMPLE_JOBS = [
    {
        "id": "j001",
        "title": "Python Backend Engineer",
        "company": "TechCorp",
        "location": "Remote",
        "description": "We are looking for a Python backend engineer with expertise in Django, Flask, or FastAPI. Strong knowledge of PostgreSQL, Redis, Docker, and AWS is required. Experience with REST APIs, CI/CD, and microservices architecture is a plus. Must know Git and Linux.",
    },
    {
        "id": "j002",
        "title": "Data Scientist",
        "company": "DataAI Labs",
        "location": "Bangalore",
        "description": "Seeking a data scientist skilled in Python, machine learning, and deep learning. Hands-on experience with scikit-learn, TensorFlow, PyTorch, pandas, and numpy. Familiarity with NLP, computer vision, SQL, and cloud platforms like AWS or GCP preferred.",
    },
    {
        "id": "j003",
        "title": "Full-Stack Developer",
        "company": "StartupXYZ",
        "location": "Mumbai",
        "description": "Full-stack developer role requiring React, Node.js/Express, TypeScript, and PostgreSQL or MongoDB. Docker, AWS, and CI/CD experience needed. Knowledge of REST APIs, GraphQL, and agile methodologies is a strong plus.",
    },
]


class TestSkillExtractor:
    """Test suite for SkillExtractor class."""

    def setup_method(self):
        self.extractor = SkillExtractor()

    def test_extract_skills_returns_dict(self):
        """Test that extract_skills returns a dictionary."""
        text = "I have experience with Python and Django"
        result = self.extractor.extract_skills(text)
        assert isinstance(result, dict)

    def test_extract_skills_finds_programming_languages(self):
        """Test that programming languages are correctly identified."""
        text = "I work with Python and JavaScript daily"
        result = self.extractor.extract_skills(text)
        assert "programming_languages" in result
        assert "python" in result["programming_languages"]
        assert "javascript" in result["programming_languages"]

    def test_extract_skills_finds_frameworks(self):
        """Test that frameworks are correctly identified."""
        text = "Experience with Django, Flask, and React"
        result = self.extractor.extract_skills(text)
        assert "web_frameworks" in result
        assert "django" in result["web_frameworks"]
        assert "flask" in result["web_frameworks"]
        assert "react" in result["web_frameworks"]

    def test_extract_skills_finds_databases(self):
        """Test that databases are correctly identified."""
        text = "Working with PostgreSQL, MongoDB, and Redis"
        result = self.extractor.extract_skills(text)
        assert "databases" in result
        assert "postgresql" in result["databases"]
        assert "mongodb" in result["databases"]
        assert "redis" in result["databases"]

    def test_extract_skill_list_returns_sorted_list(self):
        """Test that extract_skill_list returns a sorted list."""
        text = "Python, Django, PostgreSQL, Docker, AWS"
        result = self.extractor.extract_skill_list(text)
        assert isinstance(result, list)
        assert result == sorted(result)

    def test_extract_skill_list_case_insensitive(self):
        """Test that skill extraction is case insensitive."""
        text = "PYTHON python Python pYtHoN"
        result = self.extractor.extract_skill_list(text)
        assert "python" in result
        assert result.count("python") == 1  # Should not have duplicates

    def test_extract_skill_list_empty_text(self):
        """Test that empty text returns empty list."""
        result = self.extractor.extract_skill_list("")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_skill_overlap_returns_dict_structure(self):
        """Test that skill_overlap returns the correct dictionary structure."""
        result = self.extractor.skill_overlap("Python Django", "Python Flask REST API")
        assert isinstance(result, dict)
        assert "matched_skills" in result
        assert "missing_skills" in result
        assert "total_job_skills" in result
        assert "matched_count" in result
        assert "skill_match_ratio" in result

    def test_skill_overlap_perfect_match(self):
        """Test skill overlap when all job skills are in resume."""
        resume_text = "I know Python, Django, PostgreSQL"
        job_text = "Need Python, Django, PostgreSQL"
        result = self.extractor.skill_overlap(resume_text, job_text)
        assert result["skill_match_ratio"] == 1.0
        assert len(result["missing_skills"]) == 0

    def test_skill_overlap_partial_match(self):
        """Test skill overlap with partial skill match."""
        resume_text = "Python and Django"
        job_text = "Need Python, Django, PostgreSQL, Docker"
        result = self.extractor.skill_overlap(resume_text, job_text)
        assert 0.0 < result["skill_match_ratio"] < 1.0
        assert "postgresql" in result["missing_skills"]
        assert "docker" in result["missing_skills"]

    def test_skill_overlap_no_match(self):
        """Test skill overlap when no skills match."""
        resume_text = "Leadership and communication"
        job_text = "Python, Java, C++"
        result = self.extractor.skill_overlap(resume_text, job_text)
        assert result["skill_match_ratio"] == 0.0
        assert len(result["matched_skills"]) == 0

    def test_skill_overlap_matched_skills_list(self):
        """Test that matched_skills are returned as a list."""
        result = self.extractor.skill_overlap("Python, Django", "Python, Flask")
        assert isinstance(result["matched_skills"], list)
        assert "python" in result["matched_skills"]


class TestJobMatcher:
    """Test suite for JobMatcher class."""

    def setup_method(self):
        self.matcher = JobMatcher(similarity_weight=0.4, skill_weight=0.6, top_k=3)

    def test_matcher_initialization(self):
        """Test that JobMatcher initializes with correct parameters."""
        matcher = JobMatcher(similarity_weight=0.3, skill_weight=0.7, top_k=5)
        assert matcher.similarity_weight == 0.3
        assert matcher.skill_weight == 0.7
        assert matcher.top_k == 5

    def test_fit_method_trains_model(self):
        """Test that fit() trains the model on jobs."""
        self.matcher.fit(SAMPLE_JOBS)
        assert self.matcher._vectorizer is not None
        assert self.matcher._job_vectors is not None
        assert len(self.matcher._jobs) == len(SAMPLE_JOBS)

    def test_fit_stores_jobs(self):
        """Test that fit() stores the job listings."""
        self.matcher.fit(SAMPLE_JOBS)
        assert self.matcher._jobs == SAMPLE_JOBS

    def test_match_before_fit_raises_error(self):
        """Test that match() raises error if fit() not called."""
        resume_text = "Python developer with Django experience"
        with pytest.raises(Exception):
            self.matcher.match(resume_text)

    def test_match_returns_list(self):
        """Test that match() returns a list."""
        self.matcher.fit(SAMPLE_JOBS)
        results = self.matcher.match("Python Django backend developer")
        assert isinstance(results, list)

    def test_match_returns_top_k_results(self):
        """Test that match() respects top_k parameter."""
        self.matcher.fit(SAMPLE_JOBS)
        results = self.matcher.match("Python", top_k=2)
        assert len(results) <= 2

    def test_match_default_top_k(self):
        """Test that match() uses default top_k if not specified."""
        matcher = JobMatcher(top_k=2)
        matcher.fit(SAMPLE_JOBS)
        results = matcher.match("Python")
        assert len(results) <= 2

    def test_match_returns_dicts(self):
        """Test that match() returns dictionaries with expected keys."""
        self.matcher.fit(SAMPLE_JOBS)
        results = self.matcher.match("Python developer")
        assert len(results) > 0
        result = results[0]
        assert isinstance(result, dict)
        assert "job_id" in result
        assert "title" in result
        assert "company" in result
        assert "score" in result
        assert "matched_skills" in result
        assert "missing_skills" in result

    def test_match_scores_sorted_descending(self):
        """Test that results are sorted by score (descending)."""
        self.matcher.fit(SAMPLE_JOBS)
        results = self.matcher.match("Python machine learning TensorFlow")
        for i in range(len(results) - 1):
            assert results[i]["score"] >= results[i + 1]["score"]

    def test_match_with_relevant_resume(self):
        """Test match with resume text relevant to some jobs."""
        self.matcher.fit(SAMPLE_JOBS)
        python_resume = "5 years Python developer. Expertise: Django, Flask, FastAPI, PostgreSQL, Redis, Docker, AWS."
        results = self.matcher.match(python_resume)
        assert len(results) > 0
        # Python Backend Engineer job should rank high
        top_job_title = results[0]["title"]
        assert isinstance(top_job_title, str)

    def test_match_skill_info_structure(self):
        """Test that skill information is included in results."""
        self.matcher.fit(SAMPLE_JOBS)
        results = self.matcher.match("Python TensorFlow")
        if len(results) > 0:
            result = results[0]
            assert "matched_skills" in result
            assert "missing_skills" in result
            assert isinstance(result["matched_skills"], list)
            assert isinstance(result["missing_skills"], list)

    def test_match_similarity_scores(self):
        """Test that similarity scores are numeric."""
        self.matcher.fit(SAMPLE_JOBS)
        results = self.matcher.match("Python Django")
        if len(results) > 0:
            result = results[0]
            assert isinstance(result["score"], (int, float))
            assert isinstance(result["cosine_similarity"], (int, float))
            assert isinstance(result["skill_match_ratio"], (int, float))

    def test_match_scores_in_valid_range(self):
        """Test that scores are in valid range [0, 1]."""
        self.matcher.fit(SAMPLE_JOBS)
        results = self.matcher.match("Python")
        for result in results:
            assert 0.0 <= result["score"] <= 1.0
            assert 0.0 <= result["cosine_similarity"] <= 1.0
            assert 0.0 <= result["skill_match_ratio"] <= 1.0

    def test_match_with_empty_resume(self):
        """Test match with empty resume text."""
        self.matcher.fit(SAMPLE_JOBS)
        results = self.matcher.match("")
        assert isinstance(results, list)
        # Should return some results based on vectorizer

    def test_match_top_k_override(self):
        """Test overriding top_k in match() call."""
        matcher = JobMatcher(top_k=5)
        matcher.fit(SAMPLE_JOBS)
        results = matcher.match("Python", top_k=1)
        assert len(results) == 1

    def test_job_matcher_with_single_job(self):
        """Test JobMatcher with only one job."""
        single_job = [SAMPLE_JOBS[0]]
        matcher = JobMatcher()
        matcher.fit(single_job)
        results = matcher.match("Python backend")
        assert len(results) == 1

    def test_job_matcher_vectorizer_fit(self):
        """Test that TF-IDF vectorizer is properly fitted."""
        self.matcher.fit(SAMPLE_JOBS)
        # Vectorizer should transform text to vectors
        resume_text = "Python Django PostgreSQL"
        resume_vec = self.matcher._vectorizer.transform([resume_text])
        assert resume_vec.shape[0] == 1
        assert resume_vec.shape[1] > 0  # Should have features
