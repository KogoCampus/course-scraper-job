from typing import List, Optional, TypedDict
from enum import Enum

class Day(str, Enum):
    MONDAY = "mon"
    TUESDAY = "tue"
    WEDNESDAY = "wed"
    THURSDAY = "thu"
    FRIDAY = "fri"
    SATURDAY = "sat"
    SUNDAY = "sun"

class ScheduleModel(TypedDict):
    days: List[Day]
    startTime: Optional[int]         # unix timestamp
    endTime: Optional[int]           # unix timestamp

class ChildSessionModel(TypedDict):
    childSessionName: Optional[str]
    childSessionType: Optional[str]
    campus: Optional[str]
    location: Optional[str]
    schedules: List[ScheduleModel]

class SessionModel(TypedDict):
    professorName: Optional[str]     # e.g. "John Doe"
    sessionName: Optional[str]       # e.g. LEC, TUT, SEM, etc
    sessionType: Optional[str]
    campus: Optional[str]
    location: Optional[str]
    schedules: List[ScheduleModel]
    childSession: List[ChildSessionModel] # If child session exists, user must pick one. e.g. LEC D100 + TUT 001

class CourseModel(TypedDict):
    courseName: Optional[str]        # e.g. "Operating Systems"
    courseCode: Optional[str]        # e.g. "CMPT 300 D100"
    credit: Optional[float]          # Changed from Optional[int] to Optional[float]
    sessions: List[SessionModel]

class ProgramModel(TypedDict):
    programName: Optional[str]       # e.g. Computer Science
    programCode: Optional[str]       # e.g. CMPT
    courses: List[CourseModel]

class CourseListingModel(TypedDict):
    semester: str                    # e.g. Fall 2025
    programs: List[ProgramModel]
    total_programs: int
    total_courses: int
    total_sections: int
