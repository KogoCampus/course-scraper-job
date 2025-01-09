from datetime import datetime
from typing import Dict, List, Optional
import logging

from .base import BaseScraper
from app.models.course import (
    ProgramModel,
    CourseModel,
    SessionModel,
    CourseListingModel,
    Day
)

class SimonFraserUniversityScraper(BaseScraper):
    def __init__(self, task_name: str, logger: logging.Logger):
        super().__init__(task_name, logger)
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

    def _parse_days(self, days_str: Optional[str]) -> List[Day]:
        """Convert SFU day string to list of Day enums"""
        if not days_str:
            return []
            
        day_map = {
            'Mo': Day.MONDAY,
            'Tu': Day.TUESDAY,
            'We': Day.WEDNESDAY,
            'Th': Day.THURSDAY,
            'Fr': Day.FRIDAY,
            'Sa': Day.SATURDAY,
            'Su': Day.SUNDAY
        }
        
        days = []
        for i in range(0, len(days_str), 2):
            day_code = days_str[i:i+2]
            if day_code in day_map:
                days.append(day_map[day_code])
        return days

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
            self.logger.warning(f"Error fetching {url}: {str(e)}")
            return None

    def _parse_date_string(self, date_str: str) -> datetime:
        """Parse SFU date string format, handling timezone"""
        try:
            # Remove timezone abbreviation (e.g., PST, PDT) before parsing
            # Format: "Mon Jan 06 00:00:00 PST 2025" -> "Mon Jan 06 00:00:00 2025"
            date_parts = date_str.split()
            if len(date_parts) == 6:  # If format matches "Day Month Date Time TZ Year"
                date_str = f"{' '.join(date_parts[:4])} {date_parts[5]}"  # Skip TZ part
            return datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')
        except Exception as e:
            raise Exception(f"Failed to parse date string '{date_str}': {str(e)}") from e

    def _resolve_schedule_block(self, block: Dict) -> SessionModel:
        """Parse schedule block into SessionModel"""
        try:
            # Parse dates
            start_date = self._parse_date_string(block.get('startDate', ''))
            end_date = self._parse_date_string(block.get('endDate', ''))
            
            # Parse time separately and combine with date
            if block.get('startTime'):
                start_time = datetime.strptime(block.get('startTime', ''), '%H:%M').time()
                start_timestamp = int(datetime.combine(start_date.date(), start_time).timestamp())
            else:
                start_timestamp = None
                
            if block.get('endTime'):
                end_time = datetime.strptime(block.get('endTime', ''), '%H:%M').time()
                end_timestamp = int(datetime.combine(end_date.date(), end_time).timestamp())
            else:
                end_timestamp = None

            return {
                "campus": block.get('campus'),
                "days": self._parse_days(block.get('days')),
                "startTime": start_timestamp,
                "endTime": end_timestamp
            }
        except Exception as e:
            raise Exception(f"Failed to parse schedule block: {str(e)}") from e

    async def fetch_courses(self) -> CourseListingModel:
        """Fetch all course data from SFU API"""
        year = datetime.now().year
        term = self._determine_term()
        base_url = f"{self.base_url}?{year}/{term}"
        
        departments = await self._fetch_json(base_url)
        if not departments:
            return {
                "semester": f"{term.capitalize()} {year}",
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

                    # Create a new course entry for each section
                    current_course: CourseModel = {
                        "courseName": course.get('title'),
                        "courseCode": f"{program['programCode']} {course.get('text')} {section.get('value')}",  # Include section in course code
                        "professorName": None,
                        "credit": int(detail.get('units')) if detail.get('units') else None,
                        "sessions": []
                    }

                    # Get professor name from instructor info
                    instructors = detail.get('instructor', [])
                    if instructors:
                        # Get primary instructor if available, otherwise first instructor
                        primary_instructor = next(
                            (i for i in instructors if i.get('roleCode') == 'PI'),
                            instructors[0] if instructors else None
                        )
                        if primary_instructor:
                            current_course["professorName"] = primary_instructor.get('name')

                    schedule = detail.get('courseSchedule', [])
                    
                    for block in schedule:
                        if block.get('isExam'):  # Skip exam schedules
                            continue

                        try:
                            session = self._resolve_schedule_block(block)
                            current_course["sessions"].append(session)
                        except ValueError as e:
                            # Log and continue to next block
                            self.logger.warning(str(e))
                            continue
                
                    if current_course["sessions"]:  # Only add courses with sessions
                        program["courses"].append(current_course)
            
            if program["courses"]:  # Only add programs with courses
                programs.append(program)

        return {
            "semester": f"{term.capitalize()} {year}",
            "programs": programs,
            "total_programs": len(programs),
            "total_courses": sum(len(p["courses"]) for p in programs),
            "total_sections": sum(
                sum(len(c["sessions"]) for c in p["courses"])
                for p in programs
            )
        }