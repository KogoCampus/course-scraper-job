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
    
    async def save_data(self, data: any, task_name: str, file_name: str, save_path_suffix: list[str]) -> str:
        """Save course data and metadata"""
        try:
            # Construct path with optional suffixes
            path_parts = [task_name]
            path_parts.extend(save_path_suffix)
            path_parts.append(file_name)
            
            file_path = self.base_dir.joinpath(*path_parts)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            with file_path.open('w') as f:
                f.write(self._serialize_data(data))

            logger.info(f"Saved {file_name} for {task_name} at: {file_path}")
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving data for {task_name}: {str(e)}")
            raise
