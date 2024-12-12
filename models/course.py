from typing import Dict, List, Optional, TypedDict
from enum import Enum
from datetime import date, time

class WeekDay(str, Enum):
    MONDAY = "Mon"
    TUESDAY = "Tue"
    WEDNESDAY = "Wed"
    THURSDAY = "Thu"
    FRIDAY = "Fri"
    SATURDAY = "Sat"
    SUNDAY = "Sun"

class ScheduleModel(TypedDict):
    startDate: Optional[date]
    endDate: Optional[date]
    startTime: Optional[time]
    endTime: Optional[time]
    days: List[WeekDay]
    location: Optional[str]

class SectionModel(TypedDict):
    sectionName: Optional[str]
    deliveryMethod: Optional[str]
    term: Optional[str]
    activity: Optional[str]
    credits: Optional[str]
    schedule: List[ScheduleModel]

class CourseModel(TypedDict):
    courseName: Optional[str]
    courseCode: Optional[str]
    sections: List[SectionModel]

class ProgramModel(TypedDict):
    programName: Optional[str]
    programCode: Optional[str]
    courses: List[CourseModel]

class CourseListingModel(TypedDict):
    programs: List[ProgramModel]
    total_programs: int
    total_courses: int
    total_sections: int
