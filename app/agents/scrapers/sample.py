from datetime import datetime, date, time
from typing import List
import factory
from faker import Faker
import random
import logging

from .base import BaseScraper
from app.models.course import (
    ProgramModel,
    CourseModel,
    SessionModel,
    ScheduleModel,
    CourseListingModel,
    Day
)

fake = Faker()

class ScheduleFactory(factory.DictFactory):
    class Meta:
        model = ScheduleModel

    days = factory.LazyFunction(
        lambda: random.sample([
            Day.MONDAY,
            Day.TUESDAY,
            Day.WEDNESDAY,
            Day.THURSDAY,
            Day.FRIDAY
        ], random.randint(1, 3))
    )
    startTime = factory.LazyFunction(
        lambda: int(datetime.combine(
            date.today(),
            time(hour=random.randint(8, 16), minute=random.choice([0, 30]))
        ).timestamp())
    )
    endTime = factory.LazyFunction(
        lambda: int(datetime.combine(
            date.today(),
            time(hour=random.randint(17, 20), minute=random.choice([0, 30]))
        ).timestamp())
    )

class SessionFactory(factory.DictFactory):
    class Meta:
        model = SessionModel

    campus = factory.LazyFunction(lambda: random.choice(["Burnaby", "Surrey", "Vancouver"]))
    location = factory.LazyFunction(lambda: f"Building {fake.random_letter().upper()}-{fake.random_int(min=1000, max=9999)}")
    schedules = factory.LazyFunction(lambda: [ScheduleFactory() for _ in range(random.randint(1, 2))])  # 1-2 schedules per session

class CourseFactory(factory.DictFactory):
    class Meta:
        model = CourseModel

    courseName = factory.Faker('catch_phrase')
    courseCode = factory.LazyFunction(
        lambda: f"{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()} {fake.random_int(min=100, max=499)}"
    )
    professorName = factory.Faker('name')
    credit = factory.LazyFunction(lambda: random.choice([3, 4]))
    sessions = factory.LazyFunction(lambda: [SessionFactory() for _ in range(random.randint(1, 3))])  # 1-3 sessions (sections) per course

class ProgramFactory(factory.DictFactory):
    class Meta:
        model = ProgramModel

    programName = factory.Faker('job')
    programCode = factory.LazyFunction(lambda: ''.join(fake.random_letters(length=4)).upper())
    courses = factory.LazyFunction(lambda: [CourseFactory() for _ in range(random.randint(3, 8))])

class SampleScraper(BaseScraper):
    def __init__(self, task_name: str, logger: logging.Logger):
        super().__init__(task_name, logger)
        self.num_programs = random.randint(2, 5)

    async def fetch_courses(self) -> CourseListingModel:
        """Generate sample course data using factories"""
        self.logger.info(f"=== Start sample scraper ===")
        
        programs = [ProgramFactory() for _ in range(self.num_programs)]
        self.logger.info(f"Generated {len(programs)} sample programs")
        
        return {
            "semester": f"{random.choice(['Spring', 'Summer', 'Fall'])} {datetime.now().year}",
            "programs": programs,
            "total_programs": len(programs),
            "total_courses": sum(len(p["courses"]) for p in programs),
            "total_sections": sum(
                sum(len(c["sessions"]) for c in p["courses"])
                for p in programs
            )
        }
