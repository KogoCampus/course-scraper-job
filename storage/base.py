from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Union
import logging
from pathlib import Path
from datetime import datetime, date, time
import json
from enum import Enum

logger = logging.getLogger("course_scraper.storage")

class StorageEncoder(json.JSONEncoder):
    """Unified JSON encoder for all storage backends"""
    def default(self, obj: Any) -> Any:
        if isinstance(obj, (date, time, datetime)):
            return obj.isoformat()
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)

class BaseStorage(ABC):
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.timestamp = datetime.now().strftime("%Y%m%d-%H:%M:%S")

    def _serialize_data(self, data: Any) -> str:
        """Serialize data using unified encoder"""
        if isinstance(data, str):
            return data

        return json.dumps(data, cls=StorageEncoder, indent=2)

    def _get_task_dir_path(self, task_name: str, task_id: str) -> Path:
        """Get path for saving data"""
        return self.base_dir / task_name / f"{self.timestamp}-{task_id}"

    @abstractmethod
    async def save_data(self, data: any, file_name: str, task_name: str, task_id: str) -> str:
        """Save course data"""
        pass