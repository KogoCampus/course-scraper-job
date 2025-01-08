from datetime import datetime
import logging

from .base import BaseScraper
from app.models.course import CourseListingModel


class UniversityOfBritishColumbiaScraper(BaseScraper):
    def __init__(self, task_name: str, logger: logging.Logger):
        super().__init__(task_name, logger)
        self.base_url = "https://courses.students.ubc.ca/cs/courseschedule"

    def _determine_term(self) -> str:
        """Determine current term based on date"""
        month = datetime.now().month
        
        # if 1 <= month <= 4:
        #     return "Winter"
        # elif 5 <= month <= 8:
        #     return "Summer"
        # else:  # 9 <= month <= 12
        #     return "Winter"  # UBC uses Winter for Fall term
        return "SampleTerm"

    async def fetch_courses(self) -> CourseListingModel:
        """Fetch course data from UBC API"""
        year = datetime.now().year
        term = self._determine_term()
        
        self.logger.info(f"=== Start UBC scraper for {term} {year} ===")
        
        # retrieve each html page for courses from ubc website
        # https://github.com/KogoCampus/course-scraper-job/blob/dff5418512899a57492d697a596f9a6ab477ebf9/scrapers/ubc/ubcScraper.py

        # parse each html page into json using self.llm_html_parser

        # return data in foramt of models/course.py

        return {
            "semester": f"{term} {year}",
            "programs": [],
            "total_programs": 0,
            "total_courses": 0,
            "total_sections": 0
        } 