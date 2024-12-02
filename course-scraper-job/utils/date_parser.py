from datetime import datetime
from typing import Optional
import logging
import re

logger = logging.getLogger("course_scraper.date_parser")

class DateParser:
    """Utility class for parsing dates in various formats"""
    
    def __init__(self):
        # Standard date formats that can be parsed directly
        self.date_formats = [
            '%Y-%m-%d',              # 2024-09-04
            '%Y%m%d',                # 20240904
            '%a %b %d',              # Tue Dec 03
            '%a %b %d %H:%M:%S %Z %Y',  # Wed Sep 04 00:00:00 PDT/PST 2024
        ]
        
        # Patterns requiring special handling
        self.custom_date_patterns = {
            'weekday_tz': {
                'pattern': re.compile(
                    r'([A-Za-z]{3})\s+([A-Za-z]{3})\s+(\d{2})\s+(\d{2}:\d{2}:\d{2})\s+([A-Z]{3,4})\s+(\d{4})'
                ),
                'format': '%a %b %d %H:%M:%S %Y'  # Format to use after timezone removal
            }
        }

    def parse_date(self, date_str: Optional[str]) -> Optional[datetime.date]:
        """Parse date string into datetime.date object"""
        if not date_str:
            return None
            
        # Check for patterns requiring special handling
        for pattern_info in self.custom_date_patterns.values():
            if match := pattern_info['pattern'].match(date_str):
                # Remove timezone part (5th group)
                groups = match.groups()
                simplified_date = f"{groups[0]} {groups[1]} {groups[2]} {groups[3]} {groups[5]}"
                try:
                    return datetime.strptime(simplified_date, pattern_info['format']).date()
                except ValueError:
                    pass

        # Try standard formats
        for fmt in self.date_formats:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
                
        logger.warning(f"Unable to parse date: {date_str}")
        return None

    def parse_time(self, time_str: Optional[str]) -> Optional[datetime.time]:
        """Parse time string into datetime.time object"""
        if not time_str:
            return None
        try:
            return datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            logger.warning(f"Unable to parse time: {time_str}")
            return None 