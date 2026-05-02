"""
Celery Application Configuration
Background task processing for intelligence generation
"""
from celery import Celery
import os
import logging

logger = logging.getLogger(__name__)

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

# Create Celery app
try:
    celery_app = Celery(
        "marketshield",
        broker=CELERY_BROKER_URL,
        backend=CELERY_RESULT_BACKEND
    )
    
    # Configure Celery
    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,  # 5 minutes max
        task_soft_time_limit=240,  # 4 minutes soft limit
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=100,
    )
    
    celery_enabled = True
    logger.info("✅ Celery configured successfully")
    
except Exception as e:
    logger.warning(f"⚠️  Celery not available: {e}")
    logger.warning("   Background tasks disabled - using synchronous processing")
    celery_enabled = False
    celery_app = None


def is_celery_available() -> bool:
    """Check if Celery is available"""
    return celery_enabled
