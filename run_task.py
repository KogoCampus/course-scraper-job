import sys
from app.tasks.scraper_task import run_scraper

"""
CLI tool to run scraper tasks directly without Celery worker.
This is useful for local testing and development.

Usage:
    python run_task.py <task_argument>
    
Example:
    python run_task.py sample  # Runs the sample scraper
"""

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python run_task.py <school>")
        print("Example: python run_task.py sample")
        sys.exit(1)
        
    school = sys.argv[1]
    # Run the Celery task directly without going through the Celery worker
    run_scraper.apply(args=[school]).get()