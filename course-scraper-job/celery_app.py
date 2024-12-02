from celery import Celery
from config.settings import settings
from config.logging import setup_logging

# Initialize application
setup_logging(log_level=settings.LOG_LEVEL)

# Configure Celery application
celery_app = Celery(
    "course_scraper",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.scraper_task"
    ]
)

# Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour timeout
    worker_prefetch_multiplier=1,  # Disable prefetching
    task_acks_late=True,  # Tasks are acknowledged after completion
)

# Schedule scraping tasks
SCHOOLS = [
    'simon_fraser_university'
]

#@celery_app.on_after_configure.connect
#def setup_periodic_tasks(sender, **kwargs):
#    """Schedule scraping tasks for all schools"""
#    for school in SCHOOLS:
#        sender.add_periodic_task(
#            86400.0,  # 24 hours
#            run_scraper.s(school),
#            name=f'scrape-{school}'
#        )

if __name__ == '__main__':
    celery_app.start()
