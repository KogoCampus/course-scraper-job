from typing import Optional, TypedDict
from enum import Enum
from datetime import datetime

class TaskStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"

class TaskResultModel(TypedDict):
    task_name: str
    started_at: datetime
    status: TaskStatus
    data: any
    error: Optional[str]  # For failure case
