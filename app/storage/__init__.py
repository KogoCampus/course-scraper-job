from typing import Union

from .local import LocalStorage
from .s3 import S3Storage
from .base import BaseStorage
from app.config.settings import Settings

__all__ = ['LocalStorage', 'S3Storage', 'BaseStorage', 'get_storage_backend']

def get_storage_backend(settings: Settings) -> Union[LocalStorage, S3Storage]:
    """Factory function to get appropriate storage backend"""
    if settings.STORAGE_TYPE == "s3":
        return S3Storage(
            bucket=settings.S3_BUCKET,
            prefix=settings.S3_PREFIX
        )
    return LocalStorage(base_dir=settings.BASE_DIR)
