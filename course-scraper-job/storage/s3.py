import json
from datetime import datetime
from typing import Dict
import logging
import boto3
from botocore.exceptions import ClientError
from pathlib import Path

from .base import BaseStorage

logger = logging.getLogger(__name__)

class S3Storage(BaseStorage):
    def __init__(self, bucket: str, prefix: str = ""):
        super().__init__(Path(prefix) if prefix else Path())
        self.bucket = bucket
        self.s3 = boto3.client('s3')

    def _path_to_s3_key(self, path: Path) -> str:
        """Convert Path to S3 key"""
        return str(path).lstrip('/')

    async def save_data(self, data: any, file_name: str, task_name: str, task_id: str) -> str:
        """Save course data to S3"""
        try:
            path = self._get_task_dir_path(task_name, task_id) / file_name
            s3_key = self._path_to_s3_key(path)
            
            json_data = self._serialize_data(data)
            
            self.s3.put_object(
                Bucket=self.bucket,
                Key=s3_key,
                Body=json_data,
                ContentType='application/json'
            )

            logger.info(f"Saved {file_name} to S3 for {task_name} {task_id}")
            return f"s3://{self.bucket}/{s3_key}"
        except Exception as e:
            logger.error(f"Error saving data to S3 for {task_name} {task_id}: {str(e)}")
            raise

