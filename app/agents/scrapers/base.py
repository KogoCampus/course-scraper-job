from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
from typing import Dict, List
from app.models.course import CourseListingModel
from app.models.task import TaskStatus, TaskResultModel
import logging
import httpx
from app.utils.llm_html_parser import LlmHtmlParser


class BaseScraper(ABC):
    def __init__(self, task_name: str, logger: logging.Logger):
        self.task_name = task_name
        self.started_at = datetime.now()
        
        # ================================================
        # Scraper Utilities
        self.logger = logger
        self.http = self._get_http_client()
        self.llm_html_parser = LlmHtmlParser()
        # ================================================
    
    def _get_http_client(self):  
        return httpx.AsyncClient()

    @abstractmethod
    async def fetch_courses(self) -> CourseListingModel:
        """Fetch raw course data from source"""
        pass

    async def run(self) -> TaskResultModel:
        """Main execution flow"""
        try:
            data = await self.fetch_courses()
            return {
                "task_name": self.task_name,
                "started_at": self.started_at,
                "status": TaskStatus.SUCCESS,
                "data": data,
                "error": None
            }
        except Exception as e:
            self.logger.error(f"Error in {self.task_name} scraper: {str(e)}", exc_info=True)
            return {
                "task_name": self.task_name,
                "started_at": self.started_at,
                "status": TaskStatus.FAILED,
                "data": {},
                "error": str(e)
            }