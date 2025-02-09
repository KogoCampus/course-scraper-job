import json
from datetime import datetime
from typing import Dict
import logging
import boto3
from botocore.exceptions import ClientError
from pathlib import Path

from .base import BaseStorage
from app.config.settings import settings

logger = logging.getLogger(__name__)

class S3Storage(BaseStorage):
    def __init__(self, bucket: str, prefix: str = ""):
        super().__init__(Path(prefix) if prefix else Path())
        self.bucket = bucket
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )

    def _path_to_s3_key(self, path: Path) -> str:
        """Convert Path to S3 key"""
        return str(path).lstrip('/')

    async def save_data(self, data: any, task_name: str, file_name: str, save_path_suffix: list[str]) -> str:
        """Save course data to S3"""
        try:
            # Construct path with optional suffixes
            path_parts = [task_name]
            path_parts.extend(save_path_suffix)
            path_parts.append(file_name)
            
            s3_key = self._path_to_s3_key(Path(*path_parts))
            s3_path = f"s3://{self.bucket}/{s3_key}"
            
            json_data = self._serialize_data(data)
            
            self.s3.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=json_data,
                ContentType='application/json'
            )

            logger.info(f"Saved {file_name} for {task_name} at: {s3_path}")
            return s3_path
        except Exception as e:
            logger.error(f"Error saving data to S3 for {task_name}: {str(e)}")
            raise

