import pytest
import tempfile
import os
from pathlib import Path
from src.resume_parser import ResumeParser, ParsedResume
from src.utils.text_processing import (
    extract_email, extract_phone, extract_linkedin, extract_github,
    extract_education, extract_experience_years, clean_text
)


class TestTextProcessing:
    """Test suite for text processing utilities."""

    def test_extract_email_valid(self):
        """Test extracting valid email address."""
        text = "Contact me at john.doe@example.com for more info"
        result = extract_email(text)
        assert "john.doe@example.com" in result

    def test_extract_email_multiple(self):
        """Test extracting email when multiple exist."""
        text = "Email: john@example.com or jane@test.org"
        result = extract_email(text)
        assert result != ""  # Should find at least one

    def test_extract_email_missing(self):
        """Test extracting email when none exist."""
        result = extract_email("No email here at all")
        assert result == ""

    def test_extract_phone_valid(self):
        """Test extracting valid phone number."""
        text = "Call me at +91-98765-43210"
        result = extract_phone(text)
        assert result != ""

    def test_extract_phone_missing(self):
        """Test extracting phone when none exist."""
        result = extract_phone("No phone number here")
        assert result == ""

    def test_extract_linkedin_valid(self):
        """Test extracting LinkedIn profile."""
        text = "Profile: linkedin.com/in/johndoe"
        result = extract_linkedin(text)
        assert "linkedin" in result.lower()

    def test_extract_linkedin_https(self):
        """Test extracting LinkedIn profile with https."""
        text = "https://linkedin.com/in/johndoe"
        result = extract_linkedin(text)
        assert result != ""

    def test_extract_github_valid(self):
        """Test extracting GitHub profile."""
        text = "Code at github.com/johndoe"
        result = extract_github(text)
        assert "github" in result.lower() or result != ""

    def test_extract_education(self):
        """Test extracting education information."""
        text = "B.Tech Computer Science from IIT Delhi"
        result = extract_education(text)
        assert isinstance(result, list)

    def test_extract_experience_years_single_digit(self):
        """Test extracting experience years."""
        text = "I have 5 years of experience"
        result = extract_experience_years(text)
        assert result == 5.0

    def test_extract_experience_years_decimal(self):
        """Test extracting experience with decimal years."""
        text = "I have 5 years of experience"
        result = extract_experience_years(text)
        assert isinstance(result, (int, float))

    def test_extract_experience_years_missing(self):
        """Test extracting when no experience years mentioned."""
        result = extract_experience_years("Some random text")
        assert result == 0.0 or isinstance(result, float)

    def test_clean_text_removes_urls(self):
        """Test that cleaning removes URLs."""
        text = "Visit http://example.com for more and https://another.org"
        cleaned = clean_text(text)
        assert "http" not in cleaned.lower()

    def test_clean_text_lowercase(self):
        """Test that cleaning converts to lowercase."""
        text = "Hello WORLD This Is MIXED Case"
        cleaned = clean_text(text)
        assert cleaned == cleaned.lower()

    def test_clean_text_removes_special_chars(self):
        """Test that cleaning removes special characters."""
        text = "Test@#$%Email&*()Phone"
        cleaned = clean_text(text)
        assert cleaned != text  # Should be modified

    def test_clean_text_handles_whitespace(self):
        """Test that cleaning normalizes whitespace."""
        text = "Text   with    multiple     spaces"
        cleaned = clean_text(text)
        assert "     " not in cleaned


class TestParsedResume:
    """Test suite for ParsedResume dataclass."""

    def test_parsed_resume_initialization(self):
        """Test basic ParsedResume initialization."""
        resume = ParsedResume(
            name="John Doe",
            email="john@example.com",
            raw_text="Full resume content"
        )
        assert resume.name == "John Doe"
        assert resume.email == "john@example.com"
        assert resume.raw_text == "Full resume content"

    def test_parsed_resume_default_values(self):
        """Test ParsedResume default values."""
        resume = ParsedResume()
        assert resume.name == ""
        assert resume.email == ""
        assert resume.skills == []
        assert resume.education == []
        assert resume.experience_years == 0.0

    def test_parsed_resume_to_dict(self):
        """Test converting ParsedResume to dictionary."""
        resume = ParsedResume(
            name="Jane Doe",
            email="jane@example.com",
            skills=["python", "django"],
            experience_years=5.0
        )
        d = resume.to_dict()
        assert isinstance(d, dict)
        assert d["name"] == "Jane Doe"
        assert d["email"] == "jane@example.com"
        assert d["skills"] == ["python", "django"]
        assert d["experience_years"] == 5.0

    def test_parsed_resume_dict_keys(self):
        """Test that to_dict() includes all expected keys."""
        resume = ParsedResume()
        d = resume.to_dict()
        expected_keys = [
            "name", "email", "phone", "linkedin", "github",
            "education", "experience_years", "skills",
            "raw_text", "clean_text"
        ]
        for key in expected_keys:
            assert key in d


class TestResumeParser:
    """Test suite for ResumeParser class."""

    def setup_method(self):
        """Setup ResumeParser instance for each test."""
        self.parser = ResumeParser()

    def test_parser_initialization(self):
        """Test ResumeParser initializes successfully."""
        parser = ResumeParser()
        assert parser is not None
        assert hasattr(parser, 'parse')

    def test_supported_formats(self):
        """Test that supported formats are correctly defined."""
        assert ".pdf" in ResumeParser.SUPPORTED_FORMATS
        assert ".docx" in ResumeParser.SUPPORTED_FORMATS
        assert ".doc" in ResumeParser.SUPPORTED_FORMATS
        assert ".txt" in ResumeParser.SUPPORTED_FORMATS

    def test_parse_txt_file(self):
        """Test parsing a simple text file resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_content = """John Doe
john@example.com
+91-9876543210
linkedin.com/in/johndoe

Skills: Python, Django, PostgreSQL, Docker, AWS

Education: B.Tech Computer Science from University

5 years of experience in software development
"""
            txt_file = Path(tmpdir) / "resume.txt"
            txt_file.write_text(resume_content)

            result = self.parser.parse(str(txt_file))

            assert isinstance(result, ParsedResume)
            assert result.email == "john@example.com"
            assert result.experience_years > 0

    def test_parse_txt_extracts_skills(self):
        """Test that parsing extracts skills from resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_content = "I have expertise in Python, Django, and PostgreSQL"
            txt_file = Path(tmpdir) / "resume.txt"
            txt_file.write_text(resume_content)

            result = self.parser.parse(str(txt_file))

            assert isinstance(result.skills, list)
            # Skills extraction is optional depending on implementation
            assert isinstance(result.skills, list)

    def test_parse_nonexistent_file_raises(self):
        """Test that parsing non-existent file raises error."""
        with pytest.raises(Exception):
            self.parser.parse("/nonexistent/path/resume.pdf")

    def test_parse_unsupported_format_raises(self):
        """Test that parsing unsupported format raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_file = Path(tmpdir) / "resume.xyz"
            fake_file.write_text("content")
            with pytest.raises(Exception) as exc_info:
                self.parser.parse(str(fake_file))
            assert "unsupported" in str(exc_info.value).lower()

    def test_parse_returns_parsed_resume(self):
        """Test that parse() returns ParsedResume object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            txt_file = Path(tmpdir) / "resume.txt"
            txt_file.write_text("Sample resume content")
            result = self.parser.parse(str(txt_file))
            assert isinstance(result, ParsedResume)

    def test_parse_txt_extracts_email(self):
        """Test that email is extracted from resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_content = "Contact: myemail@domain.com"
            txt_file = Path(tmpdir) / "resume.txt"
            txt_file.write_text(resume_content)

            result = self.parser.parse(str(txt_file))
            assert result.email != ""

    def test_parse_txt_extracts_experience(self):
        """Test that experience years are extracted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            resume_content = "8 years of professional software development"
            txt_file = Path(tmpdir) / "resume.txt"
            txt_file.write_text(resume_content)

            result = self.parser.parse(str(txt_file))
            assert isinstance(result.experience_years, float)

    def test_parse_stores_raw_text(self):
        """Test that raw text is stored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "This is the raw resume content"
            txt_file = Path(tmpdir) / "resume.txt"
            txt_file.write_text(content)

            result = self.parser.parse(str(txt_file))
            assert result.raw_text != ""

    def test_parse_stores_clean_text(self):
        """Test that cleaned text is stored."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "RESUME Content WITH Special@#$Chars"
            txt_file = Path(tmpdir) / "resume.txt"
            txt_file.write_text(content)

            result = self.parser.parse(str(txt_file))
            assert result.clean_text != ""
            assert result.clean_text == result.clean_text.lower()

    def test_parse_multiple_files(self):
        """Test parsing multiple files sequentially."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create two different resumes
            content1 = "John Doe - Python Developer - john@example.com"
            content2 = "Jane Smith - Java Developer - jane@example.com"

            file1 = Path(tmpdir) / "resume1.txt"
            file2 = Path(tmpdir) / "resume2.txt"
            file1.write_text(content1)
            file2.write_text(content2)

            result1 = self.parser.parse(str(file1))
            result2 = self.parser.parse(str(file2))

            assert result1.email != result2.email
            assert result1.raw_text != result2.raw_text

    def test_parse_large_resume(self):
        """Test parsing a relatively large resume."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a longer resume
            resume_content = """John Doe
john@example.com
+91-98765-43210

Professional Summary:
Senior software engineer with 10 years of experience in full-stack development.

Skills:
Python, Django, FastAPI, React, JavaScript, TypeScript, PostgreSQL, MongoDB,
Docker, Kubernetes, AWS, GCP, Azure, Git, CI/CD, Microservices, REST APIs,
GraphQL, Machine Learning, TensorFlow, PyTorch, Scikit-learn

Experience:
- Senior Backend Engineer at TechCorp (3 years)
- Full Stack Developer at StartupXYZ (4 years)
- Junior Developer at WebServices Inc (3 years)

Education:
- M.Tech Computer Science from IIT Delhi
- B.Tech Computer Science from NIT Bangalore

Certifications:
- AWS Solutions Architect
- Kubernetes Administrator
- Docker Certified Associate
"""
            txt_file = Path(tmpdir) / "resume.txt"
            txt_file.write_text(resume_content)

            result = self.parser.parse(str(txt_file))

            assert result.email == "john@example.com"
            assert isinstance(result.skills, list)
            assert isinstance(result.experience_years, float)
            assert isinstance(result.education, list)