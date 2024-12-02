from datetime import datetime, date, time
from typing import Dict, List, Optional

from .base import BaseScraper
from models.course import (
    ProgramModel,
    CourseModel,
    SectionModel,
    ScheduleModel,
    CourseListingModel,
    WeekDay
)

class SimonFraserUniversityScraper(BaseScraper):
    def __init__(self, task_name: str):
        super().__init__(task_name)
        self.base_url = "https://www.sfu.ca/bin/wcm/course-outlines"

    def _determine_term(self) -> str:
        """Determine current term based on date"""
        month = datetime.now().month
        
        if 1 <= month <= 4:
            return "spring"
        elif 5 <= month <= 8:
            return "summer"
        else:  # 9 <= month <= 12
            return "fall"

    def _parse_days(self, days_str: Optional[str]) -> List[WeekDay]:
        """Convert SFU day string to list of WeekDay enums"""
        if not days_str:
            return []
            
        day_map = {
            'Mo': WeekDay.MONDAY,
            'Tu': WeekDay.TUESDAY,
            'We': WeekDay.WEDNESDAY,
            'Th': WeekDay.THURSDAY,
            'Fr': WeekDay.FRIDAY,
            'Sa': WeekDay.SATURDAY,
            'Su': WeekDay.SUNDAY
        }
        
        days = []
        for i in range(0, len(days_str), 2):
            day_code = days_str[i:i+2]
            if day_code in day_map:
                days.append(day_map[day_code])
        return days

    def _parse_date(self, date_str: Optional[str]) -> Optional[date]:
        """Convert date string to date object"""
        return self.date_parser.parse_date(date_str)

    def _parse_time(self, time_str: Optional[str]) -> Optional[time]:
        """Convert time string to time object"""
        return self.date_parser.parse_time(time_str)

    async def _fetch_json(self, url: str) -> Optional[Dict]:
        """Fetch JSON data from URL with error handling"""
        self.logger.info(f"Fetching json from {url}")
        try:
            response = await self.http.get(url)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, dict) and "errorMessage" in data:
                self.logger.warning(f"API error for {url}: {data['errorMessage']}")
                return None
                
            return data
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None

    async def fetch_courses(self) -> CourseListingModel:
        """Fetch all course data from SFU API"""
        year = datetime.now().year
        term = self._determine_term()
        base_url = f"{self.base_url}?{year}/{term}"
        
        departments = await self._fetch_json(base_url)
        if not departments:
            return {
                "programs": [],
                "total_programs": 0,
                "total_courses": 0,
                "total_sections": 0
            }

        programs: List[ProgramModel] = []
        for dept in departments:
            if not dept.get('value'):
                continue

            program: ProgramModel = {
                "programName": dept.get('name', dept.get('text')),
                "programCode": dept.get('value', '').upper(),
                "courses": []
            }

            courses_url = f"{self.base_url}?{year}/{term}/{dept['value']}"
            courses = await self._fetch_json(courses_url)
            
            if not courses:
                continue

            for course in courses:
                current_course: CourseModel = {
                    "courseName": course.get('title'),
                    "courseCode": f"{program['programCode']} {course.get('text')}",
                    "sections": []
                }

                sections_url = f"{self.base_url}?{year}/{term}/{dept['value']}/{course['value']}"
                sections = await self._fetch_json(sections_url)
                
                if not sections:
                    continue

                for section in sections:
                    if section.get('classType') != 'e':
                        continue

                    detail_url = f"{self.base_url}?{year}/{term}/{dept['value']}/{course['value']}/{section['value']}"
                    detail = await self._fetch_json(detail_url)
                    
                    if not detail:
                        continue

                    info = detail.get('info', {})
                    schedule = detail.get('courseSchedule', [])
                    
                    schedule_items: List[ScheduleModel] = []
                    for block in schedule:
                        if block.get('isExam'):  # Skip exam schedules
                            continue

                        schedule_item: ScheduleModel = {
                            "startDate": self._parse_date(block.get('startDate')),
                            "endDate": self._parse_date(block.get('endDate')),
                            "startTime": self._parse_time(block.get('startTime')),
                            "endTime": self._parse_time(block.get('endTime')),
                            "days": self._parse_days(block.get('days'))
                        }
                        schedule_items.append(schedule_item)

                    section_data: SectionModel = {
                        "sectionName": info.get('name'),
                        "deliveryMethod": info.get('deliveryMethod'),
                        "term": info.get('term'),
                        "activity": section.get('sectionCode'),
                        "credits": info.get('units'),
                        "schedule": schedule_items
                    }
                    
                    current_course["sections"].append(section_data)
                
                if current_course["sections"]:  # Only add courses with sections
                    program["courses"].append(current_course)
            
            if program["courses"]:  # Only add programs with courses
                programs.append(program)

        return {
            "programs": programs,
            "total_programs": len(programs),
            "total_courses": sum(len(p["courses"]) for p in programs),
            "total_sections": sum(
                sum(len(c["sections"]) for c in p["courses"])
                for p in programs
            )
        }