from celery import Task
from celery_app import celery_app
import logging
import asyncio
from io import StringIO
from datetime import datetime

from app.storage import get_storage_backend
from app.agents.scrapers import get_scraper_class
from app.config.settings import settings
from app.models.task import TaskStatus

class ScraperTask(Task):
    abstract = True

@celery_app.task(base=ScraperTask, name='scraper_task', bind=True)
def run_scraper(self, school: str, pageNum=-1):
    """Run scraper for specified school"""
    # Setup storage
    storage = get_storage_backend(settings)
    
    # Setup logging
    log_buffer = StringIO()
    
    # Use the standard formatter from logging config
    logger = logging.getLogger("celery.task")
    formatter = logger.handlers[0].formatter
    handler = logging.StreamHandler(log_buffer)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    try:
        # Initialize and run scraper
        scraper_cls = get_scraper_class(school)
        scraper = scraper_cls(school, logger)
        
        # Run the async code in an event loop
        loop = asyncio.get_event_loop()
        print(pageNum)
        result = loop.run_until_complete(scraper.run(index=pageNum))

        if result["status"] != TaskStatus.SUCCESS: raise Exception(result["error"])

        # Prepare metadata
        data = result["data"] if result["status"] == TaskStatus.SUCCESS else None
        current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
        storage_save_path_suffix = [school, data["semester"], f"{current_time}-{self.request.id}"]
        
        metadata = {
            "task_id": self.request.id,
            "task_name": self.name + "-" + str(pageNum),
            "started_at": result["started_at"],
            "status": result["status"],
            "error": result.get("error", None),
        }

        # Save task metadata
        loop.run_until_complete(storage.save_data(
            data=metadata,
            task_name=self.name + "-" + str(pageNum),
            file_name="metadata.json",
            save_path_suffix=storage_save_path_suffix
        ))
        
        # Save scraping results
        loop.run_until_complete(storage.save_data(
            data=data,
            task_name=self.name + "-" + str(pageNum),
            file_name="course-listing.json",
            save_path_suffix=storage_save_path_suffix
        ))

        # Save captured logs
        log_content = log_buffer.getvalue()
        if log_content:
            loop.run_until_complete(storage.save_data(
                data=log_content,
                file_name="worker.log",
                task_name=self.name + "-" + str(pageNum),
                save_path_suffix=storage_save_path_suffix
            ))
            
    except Exception as e:
        logger.error(f"Error in scraper task for {school}: {str(e)}", exc_info=True)

    finally:
        # Clean up
        logger.removeHandler(handler)
        log_buffer.close()
