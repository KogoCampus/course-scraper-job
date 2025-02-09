import logging
import asyncio
from io import StringIO
from datetime import datetime

from app.storage import get_storage_backend
from app.agents.scrapers import get_scraper_class
from app.config.settings import settings
from app.models.task import TaskStatus
from app.tasks.base import BaseTask

class ScraperTask(BaseTask):
    def __init__(self, task_name: str):
        super().__init__(task_name)
        self.logger = logging.getLogger("scraper.task")

    async def run_task(self, *args) -> dict:
        """Run scraper for specified school"""
        if not args:
            raise ValueError("School argument is required")
            
        school = args[0]
        
        # Setup storage
        storage = get_storage_backend(settings)
        log_buffer = StringIO()
        
        # Use the standard formatter from logging config
        formatter = self.logger.handlers[0].formatter
        handler = logging.StreamHandler(log_buffer)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        try:
            # Initialize and run scraper
            scraper_cls = get_scraper_class(school)
            scraper = scraper_cls(school, self.logger)
            result = await scraper.run()

            if result["status"] != TaskStatus.SUCCESS:
                raise Exception(result["error"])

            # Prepare metadata
            data = result["data"] if result["status"] == TaskStatus.SUCCESS else None
            current_time = datetime.now().strftime("%Y%m%d-%H%M%S")
            storage_save_path_suffix = [data["semester"], current_time]
            
            metadata = {
                "task_name": school,
                "started_at": result["started_at"],
                "status": result["status"],
                "error": result.get("error", None),
            }

            # Save task metadata
            await storage.save_data(
                data=metadata,
                task_name=school,
                file_name="metadata.json",
                save_path_suffix=storage_save_path_suffix
            )
            
            # Save scraping results
            await storage.save_data(
                data=data,
                task_name=school,
                file_name="course-listing.json",
                save_path_suffix=storage_save_path_suffix
            )

            # Save captured logs
            log_content = log_buffer.getvalue()
            if log_content:
                await storage.save_data(
                    data=log_content,
                    file_name="worker.log",
                    task_name=school,
                    save_path_suffix=storage_save_path_suffix
                )
                
            return result
                
        except Exception as e:
            self.logger.error(f"Error in scraper task for {school}: {str(e)}", exc_info=True)
            raise

        finally:
            # Clean up
            self.logger.removeHandler(handler)
            log_buffer.close()

# Create task instance
task = ScraperTask("scraper_task")
