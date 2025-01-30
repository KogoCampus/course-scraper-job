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
    async def fetch_courses(self, pageNum=-1) -> CourseListingModel:
        """Fetch raw course data from source"""
        pass

    async def run(self, index=-1) -> TaskResultModel:
        """Main execution flow"""
        try:
            if index != -1:
                r = []
                # fts = [asyncio.ensure_future(self.fetch_courses(pageNum=u)) for u in range(0, index)]

                # a little bit hardcoded (3)
                for i in range(3, index + 3, 3):
                    r.append(await asyncio.gather(*([asyncio.ensure_future(self.fetch_courses(pageNum=u)) for u in range(i-3,i)])))
                data = {
                    "semester": "",
                    "programs": [],
                    "total_programs": 0,
                    "total_courses": 0,
                    "total_sections": 0
                }
                for d in r:
                    data['semester'] = d['semester']
                    data['programs'].extend(d['programs'])
                    data['total_programs'] += d['total_programs']
                    data['total_courses'] += d['total_courses']
                    data['total_sections'] += d['total_sections']
            else:
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