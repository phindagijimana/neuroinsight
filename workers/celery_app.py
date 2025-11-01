"""
Celery application configuration.

This module initializes and configures the Celery application
for distributed task processing.
"""

from celery import Celery

from backend.core.config import get_settings

# Get settings
settings = get_settings()

# Create Celery application
celery_app = Celery(
    "neuroinsight",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["workers.tasks.processing", "workers.tasks.cleanup"],
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.processing_timeout,
    task_soft_time_limit=settings.processing_timeout - 300,  # 5 min before hard limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=10,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    # Periodic task scheduling (Celery Beat)
    beat_schedule={
        "cleanup-storage": {
            "task": "workers.tasks.cleanup.run_cleanup",
            "schedule": settings.cleanup_interval_hours * 3600.0,  # Convert hours to seconds
            "options": {"expires": 3600},  # Task expires after 1 hour if not executed
        },
    },
)

# Task routes - using default 'celery' queue for simplicity
# celery_app.conf.task_routes = {
#     "workers.tasks.processing.*": {"queue": "processing"},
# }

if __name__ == "__main__":
    celery_app.start()

