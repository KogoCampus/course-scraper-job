from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List
from models.course import CourseListingModel
from models.task import TaskStatus, TaskResultModel
import logging
import httpx
from utils.llm_html_parser import LlmHtmlParser
from utils.date_parser import DateParser


class BaseScraper(ABC):
    def __init__(self, task_name: str):
        self.task_name = task_name
        self.started_at = datetime.now()
        
        # ================================================
        # Scraper Utilities
        self.logger = self._get_logger()
        self.http = self._get_http_client()
        self.llm_html_parser = self._get_llm_html_parser()
        self.date_parser = self._get_date_parser()
        # ================================================
        
    def _get_logger(self):
        class_name = self.__class__.__name__
        return logging.getLogger(f"celery.task.{class_name}")

    def _get_http_client(self):  
        return httpx.AsyncClient()

    def _get_llm_html_parser(self) -> LlmHtmlParser:
        return LlmHtmlParser()

    def _get_date_parser(self) -> DateParser:
        return DateParser()
    
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
            self.logger.error(f"Error in {self.task_name} scraper: {str(e)}")
            return {
                "task_name": self.task_name,
                "started_at": self.started_at,
                "status": TaskStatus.FAILED,
                "data": {},
                "error": str(e)
            }