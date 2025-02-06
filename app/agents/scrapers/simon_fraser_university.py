from datetime import datetime
from typing import Dict, List, Optional
import logging
import pytz

from .base import BaseScraper
from app.models.course import ProgramModel, CourseModel, SessionModel, CourseListingModel, Day, ChildSessionModel

class SimonFraserUniversityScraper(BaseScraper):
    def __init__(self, task_name: str, logger: logging.Logger):
        super().__init__(task_name, logger)
        self.base_url = "https://www.sfu.ca/bin/wcm/course-outlines"
        self.pst_tz = pytz.timezone('America/Vancouver')

    def _determine_term(self) -> str:
        month = datetime.now().month
        if 1 <= month <= 4:
            return "spring"
        elif 5 <= month <= 8:
            return "summer"
        else:
            return "fall"

    def _parse_days(self, days_str: Optional[str]) -> List[Day]:
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
        try:
            date_parts = date_str.split()
            if len(date_parts) == 6:
                date_str = f"{' '.join(date_parts[:4])} {date_parts[5]}"
            return datetime.strptime(date_str, '%a %b %d %H:%M:%S %Y')
        except Exception as e:
            raise Exception(f"Failed to parse date string '{date_str}': {str(e)}") from e

    def _resolve_schedule_block(self, block: Dict) -> SessionModel:
        try:
            start_date = self._parse_date_string(block.get('startDate', ''))
            end_date = self._parse_date_string(block.get('endDate', ''))
            if block.get('startTime'):
                start_time = datetime.strptime(block.get('startTime', ''), '%H:%M').time()
                start_dt = datetime.combine(start_date.date(), start_time)
                start_dt_tz = self.pst_tz.localize(start_dt)
                start_timestamp = int(start_dt_tz.timestamp())
            else:
                start_timestamp = None
            if block.get('endTime'):
                end_time = datetime.strptime(block.get('endTime', ''), '%H:%M').time()
                end_dt = datetime.combine(end_date.date(), end_time)
                end_dt_tz = self.pst_tz.localize(end_dt)
                end_timestamp = int(end_dt_tz.timestamp())
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

    def _organize_sessions(self, sessions: List[SessionModel]) -> List[SessionModel]:
        lecture_sessions = []
        child_sessions = []
        
        for session in sessions:
            sname = session.get("sessionName", "")
            if sname.upper().startswith("LEC"):
                session["sessionType"] = "Lecture"
                session["childSession"] = []  # Initialize empty child session list
                lecture_sessions.append(session)
            elif sname.upper().startswith("TUT"):
                child_session: ChildSessionModel = {
                    "childSessionName": session.get("sessionName"),
                    "childSessionType": "Tutorial",
                    "campus": session.get("campus"),
                    "location": session.get("location"),
                    "schedules": session.get("schedules", [])
                }
                child_sessions.append(child_session)
            elif sname.upper().startswith("LAB"):
                child_session: ChildSessionModel = {
                    "childSessionName": session.get("sessionName"),
                    "childSessionType": "Laboratory",
                    "campus": session.get("campus"),
                    "location": session.get("location"),
                    "schedules": session.get("schedules", [])
                }
                child_sessions.append(child_session)
            else:
                # For other types of sessions (seminars, etc)
                session["sessionType"] = "Other"
                session["childSession"] = []
                lecture_sessions.append(session)

        # If we have both lectures and child sessions, attach child sessions to lectures
        if lecture_sessions and child_sessions:
            for lecture in lecture_sessions:
                lecture["childSession"] = child_sessions
            return lecture_sessions
        
        # If we only have lectures or other sessions without children
        if lecture_sessions:
            return lecture_sessions
        
        # If we somehow only have child sessions, convert them to regular sessions
        converted_sessions = []
        for child in child_sessions:
            session: SessionModel = {
                "sessionName": child["childSessionName"],
                "sessionType": child["childSessionType"],
                "professorName": None,
                "campus": child["campus"],
                "location": child["location"],
                "schedules": child["schedules"],
                "childSession": []
            }
            converted_sessions.append(session)
        return converted_sessions

    async def fetch_courses(self) -> CourseListingModel:
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
                current_course: CourseModel = {
                    "courseName": course.get('title'),
                    "courseCode": f"{program['programCode']} {course.get('text')}",
                    "credit": None,
                    "sessions": []
                }
                sections_url = f"{self.base_url}?{year}/{term}/{dept['value']}/{course['value']}"
                sections = await self._fetch_json(sections_url)
                if not sections:
                    continue
                for section in sections:
                    detail_url = f"{self.base_url}?{year}/{term}/{dept['value']}/{course['value']}/{section['value']}"
                    detail = await self._fetch_json(detail_url)
                    if not detail:
                        continue
                    current_session: SessionModel = {
                        "sessionName": f"{section.get('sectionCode', '')} {section.get('text', '')}".strip(),
                        "sessionType": None,  # Will be set in _organize_sessions
                        "professorName": None,
                        "campus": None,
                        "location": None,
                        "schedules": [],
                        "childSession": []  # Initialize empty child session list
                    }
                    schedule_blocks = detail.get('courseSchedule', [])
                    instructors = detail.get('instructor', [])
                    if instructors:
                        primary_instructor = next((i for i in instructors if i.get('roleCode') == 'PI'), instructors[0])
                        if primary_instructor:
                            current_session["professorName"] = primary_instructor.get('name')
                    if current_course["credit"] is None and detail.get('info', {}).get('units'):
                        current_course["credit"] = float(detail.get('info', {}).get('units'))
                    for block in schedule_blocks:
                        if block.get('isExam'):
                            continue
                        try:
                            if current_session["campus"] is None:
                                current_session["campus"] = block.get('campus')
                            start_date = self._parse_date_string(block.get('startDate', ''))
                            end_date = self._parse_date_string(block.get('endDate', ''))
                            if block.get('startTime'):
                                start_time = datetime.strptime(block.get('startTime', ''), '%H:%M').time()
                                start_dt = datetime.combine(start_date.date(), start_time)
                                start_dt_tz = self.pst_tz.localize(start_dt)
                                start_timestamp = int(start_dt_tz.timestamp())
                            else:
                                start_timestamp = None
                            if block.get('endTime'):
                                end_time = datetime.strptime(block.get('endTime', ''), '%H:%M').time()
                                end_dt = datetime.combine(end_date.date(), end_time)
                                end_dt_tz = self.pst_tz.localize(end_dt)
                                end_timestamp = int(end_dt_tz.timestamp())
                            else:
                                end_timestamp = None
                            schedule = {
                                "days": self._parse_days(block.get('days')),
                                "startTime": start_timestamp,
                                "endTime": end_timestamp
                            }
                            current_session["schedules"].append(schedule)
                        except ValueError as e:
                            self.logger.warning(str(e))
                            continue
                    if current_session["schedules"]:
                        current_course["sessions"].append(current_session)
                if current_course["sessions"]:
                    current_course["sessions"] = self._organize_sessions(current_course["sessions"])
                    program["courses"].append(current_course)
                    self.logger.info(f"Processed course: {current_course['courseCode']}")
            if program["courses"]:
                programs.append(program)
        return {
            "semester": f"{term.capitalize()} {year}",
            "programs": programs,
            "total_programs": len(programs),
            "total_courses": sum(len(p["courses"]) for p in programs),
            "total_sections": sum(sum(len(c["sessions"]) for c in p["courses"]) for p in programs)
        }
