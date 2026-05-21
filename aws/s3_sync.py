import os
import sys
import boto3
from pathlib import Path
from src.logger import logger


class S3Sync:
    """Sync local model artifacts with AWS S3."""

    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
            region_name=os.environ.get('AWS_REGION', 'ap-south-1'),
        )
        self.bucket = os.environ.get('S3_BUCKET_NAME', '')

    def upload_models(self, local_dir: str = "models"):
        """Upload all model files to S3."""
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                if file.endswith(('.pkl', '.json', '.yaml')):
                    local_path = os.path.join(root, file)
                    s3_key = local_path.replace("\\", "/")
                    self.s3.upload_file(local_path, self.bucket, s3_key)
                    logger.info(f"Uploaded: {local_path} → s3://{self.bucket}/{s3_key}")

    def download_models(self, local_dir: str = "models"):
        """Download model files from S3 to local."""
        paginator = self.s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=self.bucket, Prefix="models/"):
            for obj in page.get('Contents', []):
                s3_key = obj['Key']
                local_path = s3_key
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                self.s3.download_file(self.bucket, s3_key, local_path)
                logger.info(f"Downloaded: s3://{self.bucket}/{s3_key} → {local_path}")

    def sync_artifacts(self, direction: str = "upload"):
        """Sync artifacts/ directory with S3."""
        if direction == "upload":
            self.upload_models("artifacts")
        else:
            self.download_models("artifacts")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "upload"
    syncer = S3Sync()
    if action == "upload":
        syncer.upload_models()
    elif action == "download":
        syncer.download_models()
    print(f"S3 sync ({action}) complete.")