import json
import os
from typing import List, Dict
from src.logger import logger
from src.exception import ResumeScreenerException

RAW_DIR = "dataset/raw"

SAMPLE_JOBS: List[Dict] = [
    {"id": "j001", "title": "Python Backend Engineer", "company": "TechCorp", "location": "Remote", "description": "We are looking for a Python backend engineer with expertise in Django, Flask, or FastAPI. Strong knowledge of PostgreSQL, Redis, Docker, and AWS is required. Experience with REST APIs, CI/CD, and microservices architecture is a plus. Must know Git and Linux."},
    {"id": "j002", "title": "Data Scientist", "company": "DataAI Labs", "location": "Bangalore", "description": "Seeking a data scientist skilled in Python, machine learning, and deep learning. Hands-on experience with scikit-learn, TensorFlow, PyTorch, pandas, and numpy. Familiarity with NLP, computer vision, SQL, and cloud platforms like AWS or GCP preferred."},
    {"id": "j003", "title": "Full-Stack Developer", "company": "StartupXYZ", "location": "Mumbai", "description": "Full-stack developer role requiring React, Node.js/Express, TypeScript, and PostgreSQL or MongoDB. Docker, AWS, and CI/CD experience needed. Knowledge of REST APIs, GraphQL, and agile methodologies is a strong plus."},
    {"id": "j004", "title": "DevOps Engineer", "company": "CloudBase", "location": "Hyderabad", "description": "DevOps engineer with Kubernetes, Docker, Terraform, and Ansible. Experience with Jenkins or GitLab CI/CD pipelines. Proficiency in Linux, Bash scripting, AWS or Azure. Monitoring with Prometheus and Grafana is desirable."},
    {"id": "j005", "title": "Machine Learning Engineer", "company": "AI Ventures", "location": "Remote", "description": "ML engineer to design and productionise models using Python, TensorFlow, PyTorch, and scikit-learn. Experience with MLOps, Airflow, Spark, and SQL databases. Strong understanding of NLP and computer vision algorithms. AWS or GCP deployment experience."},
    {"id": "j006", "title": "Frontend Developer", "company": "UIcraft", "location": "Pune", "description": "Frontend developer with strong React, TypeScript, HTML, CSS, Tailwind, and Sass skills. Experience with Next.js, REST APIs, GraphQL, and agile/scrum workflows. Nice to have: Vue or Angular."},
    {"id": "j007", "title": "Data Engineer", "company": "PipelineHQ", "location": "Chennai", "description": "Data engineer experienced in Python, Spark, Kafka, Airflow, and dbt. Must have strong SQL skills and experience with PostgreSQL or BigQuery. AWS or GCP cloud experience essential. Docker and Kubernetes knowledge preferred."},
    {"id": "j008", "title": "Software Engineer Java", "company": "FinTech Ltd", "location": "Delhi", "description": "Java backend engineer with Spring Boot, microservices, REST APIs, and SQL/PostgreSQL expertise. Experience with Kafka, Redis, Docker, Kubernetes, and CI/CD pipelines. Agile/scrum environment."},
]

class DataIngestion:
    def __init__(self, raw_dir: str = RAW_DIR):
        self.raw_dir = raw_dir

    def initiate_data_ingestion(self) -> List[Dict]:
        logger.info("Starting data ingestion...")
        jobs: List[Dict] = []
        if os.path.isdir(self.raw_dir):
            for fname in os.listdir(self.raw_dir):
                if fname.endswith(".json"):
                    try:
                        with open(os.path.join(self.raw_dir, fname)) as f:
                            data = json.load(f)
                        if isinstance(data, list):
                            jobs.extend(data)
                        elif isinstance(data, dict):
                            jobs.append(data)
                    except Exception as e:
                        logger.warning(f"Skipping {fname}: {e}")
        if not jobs:
            logger.info("No job files found — using built-in sample dataset.")
            jobs = SAMPLE_JOBS
        logger.info(f"Data ingestion complete. {len(jobs)} jobs loaded.")
        return jobs