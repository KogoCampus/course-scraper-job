from celery import Celery
from celery.schedules import crontab
from app.config.settings import settings
from app.config.logging import setup_logging

# Initialize application
setup_logging(log_level=settings.LOG_LEVEL)

# Configure Celery application
celery_app = Celery(
    "course_scraper",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.scraper_task"
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
    worker_pool_restarts=True,  # Enable worker pool restarts
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks
    worker_autoscaler='celery.worker.autoscale:Autoscaler',  # Enable autoscaling
    worker_autoscale_max=3,  # Maximum number of workers
    worker_autoscale_min=1,  # Minimum number of workers
)

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    'scrape-sfu-monthly': {
        'task': 'app.tasks.scraper_task.run_scraper',
        'schedule': crontab(0, 0, day_of_month='1'),  # Run at midnight on the 1st of every month
        'args': ('simon_fraser_university',)
    },
    'scrape-ubc-monthly': {
        'task': 'app.tasks.scraper_task.run_scraper',
        'schedule': crontab(0, 0, day_of_month='1'),  # Run at midnight on the 1st of every month
        'args': ('university_of_british_columbia',)
    }
}


if __name__ == '__main__':
    celery_app.start()
