from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # Storage settings
    STORAGE_TYPE: str = "local"
    ## local storage settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent / "local"
    ## s3 storage settings
    S3_BUCKET: str = "course-scraper-storage"
    S3_PREFIX: str = "course_data"

    # LLM settings
    LLM_MODEL: str = "mistral/mistral-medium"
    MISTRAL_API_KEY: Optional[str] = None

    # AWS settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None

    # Redis settings
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False

    # Celery settings
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    # Flower authentication settings
    FLOWER_BASIC_AUTH_USERNAME: str = "admin"
    FLOWER_BASIC_AUTH_PASSWORD: str = "password"

    class Config:
        env_file = (Path(__file__).parent.parent / '.env',)
        env_file_encoding = 'utf-8'

settings = Settings()