import sys
import os
import asyncio
import importlib
import traceback
from typing import List
from app.config.logging import setup_logging

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

"""
CLI tool to run tasks directly.
This is useful for local testing and development.

Usage:
    python run_task.py <task_name> [task_arguments...]
    
Example:
    python run_task.py scraper_task sample  # Runs the scraper_task.py with 'sample' as argument
"""

async def run_task(task_name: str, args: List[str]):
    try:
        # Setup logging first
        setup_logging()
        
        # Dynamically import the task module
        task_module = importlib.import_module(f"app.tasks.{task_name}")
        
        # Get the task instance (each task module should have a 'task' instance)
        task = getattr(task_module, "task")
        
        # Run the task with provided arguments
        await task.run_task(*args)
        
        # Only print task completion status without the full result
        print(f"Task completed successfully")
    except ImportError as e:
        print(f"Error: Task '{task_name}' not found")
        print("Stack trace:")
        traceback.print_exc()
        sys.exit(1)
    except AttributeError as e:
        print(f"Error: Task '{task_name}' does not have a task instance")
        print("Stack trace:")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"Task failed: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_task.py task_name [task_arguments...]")
        print("Example: python run_task.py scraper_task sample")
        sys.exit(1)
        
    task_name = sys.argv[1]
    task_args = sys.argv[2:]
    
    try:
        asyncio.run(run_task(task_name, task_args))
    except KeyboardInterrupt:
        print("\nTask interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        print("Stack trace:")
        traceback.print_exc()
        sys.exit(1)