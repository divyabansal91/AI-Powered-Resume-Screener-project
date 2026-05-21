import sys
import os
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, field

from src.logger import logger
from src.exception import ResumeScreenerException
from src.utils.text_processing import (
    extract_email, extract_phone, extract_linkedin,
    extract_github, extract_education, extract_experience_years,
    clean_text
)


@dataclass
class ParsedResume:
    raw_text: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    education: list = field(default_factory=list)
    experience_years: float = 0.0
    skills: list = field(default_factory=list)
    clean_text: str = ""

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "linkedin": self.linkedin,
            "github": self.github,
            "education": self.education,
            "experience_years": self.experience_years,
            "skills": self.skills,
            "raw_text": self.raw_text,
            "clean_text": self.clean_text,
        }


class ResumeParser:
    """Parse resumes from PDF or DOCX files."""

    SUPPORTED_FORMATS = [".pdf", ".docx", ".doc", ".txt"]

    def __init__(self):
        logger.info("ResumeParser initialized")

    def parse(self, file_path: str) -> ParsedResume:
        """Main entry point — detects file type and parses."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")

            ext = path.suffix.lower()
            if ext not in self.SUPPORTED_FORMATS:
                raise ValueError(f"Unsupported format: {ext}. Supported: {self.SUPPORTED_FORMATS}")

            logger.info(f"Parsing resume: {path.name} [{ext}]")

            if ext == ".pdf":
                raw_text = self._parse_pdf(file_path)
            elif ext in [".docx", ".doc"]:
                raw_text = self._parse_docx(file_path)
            else:
                raw_text = self._parse_txt(file_path)

            return self._extract_fields(raw_text)

        except Exception as e:
            raise ResumeScreenerException(e, sys)

    def _parse_pdf(self, file_path: str) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            import pdfplumber
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            logger.info(f"PDF parsed — {len(text)} characters extracted")
            return text
        except ImportError:
            raise ImportError("pdfplumber not installed. Run: pip install pdfplumber")

    def _parse_docx(self, file_path: str) -> str:
        """Extract text from DOCX using python-docx."""
        try:
            from docx import Document
            doc = Document(file_path)
            paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
            text = "\n".join(paragraphs)
            logger.info(f"DOCX parsed — {len(text)} characters extracted")
            return text
        except ImportError:
            raise ImportError("python-docx not installed. Run: pip install python-docx")

    def _parse_txt(self, file_path: str) -> str:
        """Read plain text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def _extract_fields(self, raw_text: str) -> ParsedResume:
        """Extract structured fields from raw text."""
        resume = ParsedResume()
        resume.raw_text = raw_text
        resume.clean_text = clean_text(raw_text)
        resume.email = extract_email(raw_text)
        resume.phone = extract_phone(raw_text)
        resume.linkedin = extract_linkedin(raw_text)
        resume.github = extract_github(raw_text)
        resume.education = extract_education(raw_text)
        resume.experience_years = extract_experience_years(raw_text)
        resume.name = self._extract_name(raw_text)
        logger.info(f"Fields extracted — email: {resume.email}, phone: {resume.phone}")
        return resume

    def _extract_name(self, text: str) -> str:
        """Heuristic: first non-empty line is usually the name."""
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        if lines:
            first_line = lines[0]
            # Reject if it looks like a heading or URL
            if len(first_line.split()) <= 5 and not any(
                c in first_line for c in ['@', 'http', '.com', '.in']
            ):
                return first_line
        return ""

    def parse_from_bytes(self, file_bytes: bytes, filename: str) -> ParsedResume:
        """Parse resume from in-memory bytes (for Flask upload)."""
        import tempfile
        try:
            suffix = Path(filename).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            result = self.parse(tmp_path)
            os.unlink(tmp_path)
            return result
        except Exception as e:
            raise ResumeScreenerException(e, sys)