from abc import ABC, abstractmethod
from typing import Any, List

class BaseTask(ABC):
    """Base class for all tasks"""
    
    def __init__(self, task_name: str):
        self.task_name = task_name
    
    @abstractmethod
    async def run_task(self, *args: List[str]) -> Any:
        """
        Main task execution method that all tasks must implement
        
        Args:
            *args: Variable length argument list passed to the task
            
        Returns:
            Any: Task execution result
        """
        pass 