from setuptools import setup, find_packages

setup(
    name="ai-resume-screener",
    version="1.0.0",
    author="Your Name",
    author_email="your@email.com",
    description="AI-powered resume screening and job recommendation system",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "flask>=3.0.0",
        "pdfplumber>=0.11.0",
        "python-docx>=1.1.0",
        "scikit-learn>=1.5.0",
        "numpy>=1.26.0",
        "pandas>=2.2.0",
        "python-box>=7.0.0",
        "PyYAML>=6.0.0",
        "python-dotenv>=1.0.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
    ],
)