from datetime import datetime, timedelta, date, time
from typing import List
import factory
from faker import Faker
import random

from .base import BaseScraper
from models.course import (
    ProgramModel,
    CourseModel,
    SectionModel,
    ScheduleModel,
    CourseListingModel,
    WeekDay
)

fake = Faker()

class ScheduleFactory(factory.DictFactory):
    class Meta:
        model = ScheduleModel

    @factory.lazy_attribute
    def startDate(self) -> date:
        return fake.date_between(start_date='+30d', end_date='+60d')

    @factory.lazy_attribute
    def endDate(self) -> date:
        start_date = self.startDate
        return (datetime.combine(start_date, time.min) + timedelta(days=90)).date()

    @factory.lazy_attribute
    def startTime(self) -> time:
        hour = random.randint(8, 16)
        minute = random.choice([0, 30])
        return time(hour=hour, minute=minute)

    @factory.lazy_attribute
    def endTime(self) -> time:
        start_dt = datetime.combine(date.today(), self.startTime)
        duration = timedelta(hours=random.choice([1, 1.5, 2]))
        end_dt = start_dt + duration
        return end_dt.time()

    @factory.lazy_attribute
    def days(self) -> List[WeekDay]:
        num_days = random.randint(1, 3)
        return random.sample([
            WeekDay.MONDAY,
            WeekDay.TUESDAY,
            WeekDay.WEDNESDAY,
            WeekDay.THURSDAY,
            WeekDay.FRIDAY
        ], num_days)

    @factory.lazy_attribute
    def location(self) -> str:
        return random.choice(["Burnaby", "Surrey", "Vancouver"])

class SectionFactory(factory.DictFactory):
    class Meta:
        model = SectionModel

    sectionName = factory.LazyFunction(lambda: f"{random.choice(['D', 'E', 'G'])}{fake.random_int(min=100, max=999)}")
    deliveryMethod = factory.LazyFunction(lambda: random.choice(["In Person", "Remote", "Hybrid"]))
    term = factory.LazyFunction(lambda: f"{random.choice(['Spring', 'Summer', 'Fall'])} {fake.year()}")
    activity = factory.LazyFunction(lambda: random.choice(["LEC", "TUT", "LAB", "SEM"]))
    credits = factory.LazyFunction(lambda: str(random.choice([3, 4])))
    schedule = factory.LazyFunction(lambda: [ScheduleFactory() for _ in range(random.randint(1, 3))])

class CourseFactory(factory.DictFactory):
    class Meta:
        model = CourseModel

    courseName = factory.Faker('catch_phrase')
    courseCode = factory.LazyFunction(lambda: f"{fake.random_letter().upper()}{fake.random_letter().upper()}{fake.random_letter().upper()} {fake.random_int(min=100, max=499)}")
    sections = factory.LazyFunction(lambda: [SectionFactory() for _ in range(random.randint(1, 4))])

class ProgramFactory(factory.DictFactory):
    class Meta:
        model = ProgramModel

    programName = factory.Faker('job')
    programCode = factory.LazyFunction(lambda: ''.join(fake.random_letters(length=4)).upper())
    courses = factory.LazyFunction(lambda: [CourseFactory() for _ in range(random.randint(3, 8))])

class SampleScraper(BaseScraper):
    def __init__(self, task_name: str):
        super().__init__(task_name)
        self.num_programs = random.randint(2, 5)

    async def fetch_courses(self) -> CourseListingModel:
        """Generate sample course data using factories"""
        self.logger.info(f"=== Start sample scraper ===")
        
        programs = [ProgramFactory() for _ in range(self.num_programs)]
        self.logger.info(f"Generated {len(programs)} sample programs")
        
        return {
            "programs": programs,
            "total_programs": len(programs),
            "total_courses": sum(len(p["courses"]) for p in programs),
            "total_sections": sum(
                sum(len(c["sections"]) for c in p["courses"])
                for p in programs
            )
        }
