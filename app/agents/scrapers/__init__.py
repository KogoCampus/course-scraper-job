from typing import Type
from .base import BaseScraper
from .simon_fraser_university import SimonFraserUniversityScraper
from .sample import SampleScraper
from .university_of_british_columbia import *

SCRAPER_MAP = {
    'sample': SampleScraper,
    'simon_fraser_university': SimonFraserUniversityScraper,
    'university_of_british_columbia': UniversityOfBritishColumbiaScraper,
}

def get_scraper_class(school: str) -> Type[BaseScraper]:
    """Get appropriate scraper class for school"""
    scraper_cls = SCRAPER_MAP.get(school.lower())
    if not scraper_cls:
        raise ValueError(f"No scraper found for school: {school}")
    return scraper_cls
