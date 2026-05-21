import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name = "resume_screener"

list_of_files = [
    ".github/workflows/ci.yml",
    f"src/__init__.py",
    f"src/components/__init__.py",
    f"src/components/data_ingestion.py",
    f"src/components/data_preprocessing.py",
    f"src/components/feature_engineering.py",
    f"src/components/model_trainer.py",
    f"src/components/model_evaluator.py",
    f"src/pipeline/__init__.py",
    f"src/pipeline/training_pipeline.py",
    f"src/pipeline/prediction_pipeline.py",
    f"src/utils/__init__.py",
    f"src/utils/common.py",
    f"src/utils/text_processing.py",
    f"src/resume_parser.py",
    f"src/job_matcher.py",
    f"src/skill_extractor.py",
    f"src/exception.py",
    f"src/logger.py",
    "config/config.yaml",
    "config/logging.yaml",
    "dataset/raw/.gitkeep",
    "dataset/processed/.gitkeep",
    "artifacts/raw/.gitkeep",
    "artifacts/processed/.gitkeep",
    "artifacts/reports/.gitkeep",
    "models/resume_parser/.gitkeep",
    "models/job_matcher/.gitkeep",
    "models/skill_extractor/.gitkeep",
    "tests/unit/__init__.py",
    "tests/unit/test_parser.py",
    "tests/unit/test_matcher.py",
    "tests/integration/__init__.py",
    "tests/integration/test_api.py",
    "templates/index.html",
    "templates/result.html",
    "templates/upload.html",
    "static/css/.gitkeep",
    "static/js/.gitkeep",
    "aws/ec2_setup.sh",
    "aws/s3_sync.py",
    "notebooks/01_eda.ipynb",
    "notebooks/02_preprocessing.ipynb",
    "notebooks/03_model_experiments.ipynb",
    "app.py",
    "Dockerfile",
    "docker-compose.yml",
    "requirements.txt",
    "requirements-dev.txt",
    "setup.py",
    "params.yaml",
    "dvc.yaml",
    ".env.example",
    ".gitignore",
    "README.md",
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for file: {filename}")

    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, 'w') as f:
            pass  # empty file
        logging.info(f"Creating empty file: {filepath}")
    else:
        logging.info(f"{filename} already exists")