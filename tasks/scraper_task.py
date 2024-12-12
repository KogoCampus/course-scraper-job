from celery import Task
from celery_app import celery_app
from storage import get_storage_backend
from scrapers import get_scraper_class
from config.settings import settings
from models.task import TaskStatus
from config.logging import setup_logging
import logging
import asyncio
from io import StringIO
from datetime import datetime

logger = logging.getLogger("celery.task")

class ScraperTask(Task):
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle task failure - only for catastrophic failures where run() couldn't complete"""
        logger.error(f"Task {task_id} failed catastrophically: {str(exc)}")

@celery_app.task(base=ScraperTask, name='scraper_task', bind=True)
def run_scraper(self, school: str):
    """Run scraper for specified school"""
    task_name = f"{self.name}/{school}"

    storage = get_storage_backend(settings)
    log_buffer = StringIO()
    
    # Use the standard formatter from logging config
    formatter = logger.handlers[0].formatter
    handler = logging.StreamHandler(log_buffer)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    
    try:
        # Initialize and run scraper
        scraper_cls = get_scraper_class(school)
        scraper = scraper_cls(school)
        
        # Run the async code in an event loop
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(scraper.run())
        
        # Prepare metadata
        data = result["data"] if result["status"] == TaskStatus.SUCCESS else None
        metadata = {
            "task_id": self.request.id,
            "task_name": result["task_name"],
            "started_at": result["started_at"],
            "status": result["status"],
            "error": result.get("error", None),
            "total_programs": data["total_programs"] if result["status"] == TaskStatus.SUCCESS else None,
            "total_courses": data["total_courses"] if result["status"] == TaskStatus.SUCCESS else None,
            "total_sections": data["total_sections"] if result["status"] == TaskStatus.SUCCESS else None
        }
        loop.run_until_complete(storage.save_data(
            data=metadata,
            file_name="metadata.json",
            task_name=task_name,
            task_id=self.request.id
        ))

        if result["status"] == TaskStatus.SUCCESS:
            # Save course data
            loop.run_until_complete(storage.save_data(
                data=data["programs"],
                file_name="course-listing.json",
                task_name=task_name,
                task_id=self.request.id
            ))
        else:
            logger.error(f"Scraper failed for {school}: {metadata['error']}")
            
        return self.request.id
    except Exception as e:
        logger.error(f"Error in scraper task for {school} {self.request.id}: {str(e)}", exc_info=True)
        raise
    finally:
        # Save captured logs
        log_content = log_buffer.getvalue()
        if log_content:
            loop.run_until_complete(storage.save_data(
                data=log_content,
                file_name="worker.log",
                task_name=task_name,
                task_id=self.request.id
            ))
            
        # Clean up
        logger.removeHandler(handler)
        log_buffer.close()
            