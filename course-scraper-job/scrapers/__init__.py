from typing import Type
from .base import BaseScraper
from .simon_fraser_university import SimonFraserUniversityScraper
from .sample import SampleScraper

SCRAPER_MAP = {
    'sample': SampleScraper,
    'simon_fraser_university': SimonFraserUniversityScraper,
}

def get_scraper_class(school: str) -> Type[BaseScraper]:
    """Get appropriate scraper class for school"""
    scraper_cls = SCRAPER_MAP.get(school.lower())
    if not scraper_cls:
        raise ValueError(f"No scraper found for school: {school}")
    return scraper_cls
