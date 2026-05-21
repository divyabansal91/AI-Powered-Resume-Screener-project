import re
import sys
import string
from typing import List
from src.logger import logger
from src.exception import ResumeScreenerException


def clean_text(text: str) -> str:
    """Remove extra whitespace, special chars, and normalize text."""
    try:
        text = text.lower()
        text = re.sub(r'http\S+|www\S+', '', text)          # remove URLs
        text = re.sub(r'\S+@\S+', '', text)                  # remove emails
        text = re.sub(r'\+?\d[\d\s\-().]{7,}\d', '', text)  # remove phone numbers
        text = re.sub(r'[^\w\s]', ' ', text)                 # remove punctuation
        text = re.sub(r'\s+', ' ', text).strip()             # collapse whitespace
        return text
    except Exception as e:
        raise ResumeScreenerException(e, sys)


def extract_email(text: str) -> str:
    """Extract first email from text."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group() if match else ""


def extract_phone(text: str) -> str:
    """Extract first phone number from text."""
    pattern = r'\+?\d[\d\s\-().]{7,}\d'
    match = re.search(pattern, text)
    return match.group().strip() if match else ""


def extract_linkedin(text: str) -> str:
    """Extract LinkedIn URL from text."""
    pattern = r'linkedin\.com/in/[\w\-]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group() if match else ""


def extract_github(text: str) -> str:
    """Extract GitHub URL from text."""
    pattern = r'github\.com/[\w\-]+'
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group() if match else ""


def extract_education(text: str) -> List[str]:
    """Extract education-related keywords from text."""
    degrees = [
        "b.tech", "m.tech", "btech", "mtech", "bachelor", "master",
        "phd", "ph.d", "b.sc", "m.sc", "bsc", "msc", "mba", "be", "me",
        "b.e", "m.e", "diploma", "b.com", "m.com",
    ]
    found = []
    text_lower = text.lower()
    for degree in degrees:
        if degree in text_lower:
            found.append(degree.upper())
    return list(set(found))


def extract_experience_years(text: str) -> float:
    """Extract years of experience mentioned in text."""
    patterns = [
        r'(\d+)\+?\s*years?\s*of\s*experience',
        r'experience\s*of\s*(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s*of\s*experience',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return 0.0


def tokenize(text: str) -> List[str]:
    """Simple whitespace tokenizer after cleaning."""
    return clean_text(text).split()


def remove_stopwords(tokens: List[str], stopwords: List[str] = None) -> List[str]:
    """Remove stopwords from token list."""
    if stopwords is None:
        stopwords = [
            "a", "an", "the", "and", "or", "but", "in", "on", "at",
            "to", "for", "of", "with", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does",
            "did", "will", "would", "could", "should", "may", "might",
            "shall", "can", "need", "dare", "ought", "used",
        ]
    return [t for t in tokens if t not in stopwords]