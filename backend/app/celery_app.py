from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "trading_platform",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]  # Will be created in Phase 4
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Optional: Add periodic tasks (for Phase 5 - Live Trading)
celery_app.conf.beat_schedule = {}

if __name__ == "__main__":
    celery_app.start()
