import logging
import logging.config
import sys
from typing import Optional

def setup_logging(log_level: str = "INFO") -> None:
    """Configure logging for the application"""
    
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": sys.stdout,
            }
        },
        "loggers": {
            "": {  # Root logger
                "handlers": ["console"],
                "level": log_level,
            },
            "scraper.task": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            }
        }
    }

    logging.config.dictConfig(config)
