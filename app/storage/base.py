from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, Union
import logging
from pathlib import Path
from datetime import datetime, date, time
import json
from enum import Enum

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
        # Calculate reverse year (9999 - current_year) for sorting
        now = datetime.now()
        reverse_year = 9999 - now.year
        # Format: {reverse_year}{month:02d}{day:02d}-{hour:02d}{minute:02d}{second:02d}
        # this is for reversing S3 sorting criteria (alphabetic order)
        self.timestamp = f"{reverse_year:04d}{now.month:02d}{now.day:02d}-{now.hour:02d}{now.minute:02d}{now.second:02d}"

    def _serialize_data(self, data: Any) -> str:
        """Serialize data using unified encoder"""
        if isinstance(data, str):
            return data
        return json.dumps(data, cls=StorageEncoder, indent=2)

    def _get_task_dir_path(self, task_name: str) -> Path:
        """Get path for saving data"""
        return self.base_dir / task_name

    @abstractmethod
    async def save_data(self, data: any, task_name: str, file_name: str, save_path_suffix: list[str]) -> str:
        """Save course data"""
        pass
