from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Base settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent / "local"
    ENV: str = "development"

    # Storage settings
    STORAGE_TYPE: str = "local"
    S3_BUCKET: Optional[str] = None
    S3_PREFIX: str = "course_data"

    # LLM settings
    LLM_MODEL: str = "mistral/mistral-medium"
    MISTRAL_API_KEY: Optional[str] = None
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

    # Logging settings
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ('.env', 'local.env')

settings = Settings()