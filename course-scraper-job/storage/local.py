import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import logging

from .base import BaseStorage

logger = logging.getLogger(__name__)

class LocalStorage(BaseStorage):
    def __init__(self, base_dir: Path):
        super().__init__(base_dir)
    
    async def save_data(self, data: any, file_name: str, task_name: str, task_id: str) -> str:
        """Save course data and metadata"""
        try:
            file_path = self._get_task_dir_path(task_name, task_id) / file_name
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with file_path.open('w') as f:
                f.write(self._serialize_data(data))

            logger.info(f"Saved {file_name} for {task_name} {task_id}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving data for {task_name} {task_id}: {str(e)}")
            raise
