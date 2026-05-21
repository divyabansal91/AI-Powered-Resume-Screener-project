import pytest
import tempfile
import os
from src.resume_parser import ResumeParser, ParsedResume
from src.utils.text_processing import (
    extract_email, extract_phone, extract_linkedin,
    extract_experience_years, clean_text
)


class TestTextProcessing:

    def test_extract_email(self):
        text = "Contact me at john.doe@example.com for more info"
        assert extract_email(text) == "john.doe@example.com"

    def test_extract_email_missing(self):
        assert extract_email("No email here") == ""

    def test_extract_phone(self):
        text = "Call me at +91 98765 43210"
        result = extract_phone(text)
        assert result != ""

    def test_extract_linkedin(self):
        text = "Profile: linkedin.com/in/johndoe"
        assert extract_linkedin(text) == "linkedin.com/in/johndoe"

    def test_extract_experience_years(self):
        text = "I have 3 years of experience in Python"
        assert extract_experience_years(text) == 3.0

    def test_clean_text_removes_urls(self):
        text = "Visit http://example.com for more"
        assert "http" not in clean_text(text)

    def test_clean_text_lowercase(self):
        result = clean_text("Hello WORLD")
        assert result == result.lower()


class TestResumeParser:

    def setup_method(self):
        self.parser = ResumeParser()

    def test_parse_txt_file(self, tmp_path):
        # Create a temp .txt resume
        resume_content = """John Doe
john@example.com
+91 9876543210
linkedin.com/in/johndoe
github.com/johndoe

Skills: Python, Machine Learning, TensorFlow, Docker

Education: B.Tech Computer Science

3 years of experience in software development
"""
        txt_file = tmp_path / "resume.txt"
        txt_file.write_text(resume_content)

        result = self.parser.parse(str(txt_file))

        assert isinstance(result, ParsedResume)
        assert result.email == "john@example.com"
        assert "linkedin.com/in/johndoe" in result.linkedin
        assert result.experience_years == 3.0

    def test_unsupported_format_raises(self, tmp_path):
        fake = tmp_path / "resume.xyz"
        fake.write_text("content")
        with pytest.raises(Exception):
            self.parser.parse(str(fake))

    def test_file_not_found_raises(self):
        with pytest.raises(Exception):
            self.parser.parse("nonexistent_file.pdf")

    def test_parsed_resume_to_dict(self):
        r = ParsedResume(name="Jane", email="jane@test.com")
        d = r.to_dict()
        assert d["name"] == "Jane"
        assert d["email"] == "jane@test.com"
        assert "skills" in d