"""Celery application configuration."""

from celery import Celery


def _get_settings():
    """Lazy load settings to avoid import errors during module loading."""
    from app.config import settings
    return settings


celery_app = Celery("food_delivery")

# Configure Celery lazily
def configure_celery():
    """Configure Celery with settings."""
    settings = _get_settings()
    
    celery_app.conf.broker_url = settings.redis_url
    celery_app.conf.result_backend = settings.redis_url
    celery_app.conf.timezone = settings.timezone
    celery_app.conf.task_serializer = "json"
    celery_app.conf.accept_content = ["json"]
    celery_app.conf.result_serializer = "json"
    celery_app.conf.enable_utc = True
    celery_app.conf.task_track_started = True
    celery_app.conf.task_time_limit = 30 * 60  # 30 minutes
    celery_app.conf.worker_prefetch_multiplier = 1
    celery_app.conf.worker_max_tasks_per_child = 1000


# Include task modules
celery_app.conf.include = [
    "app.tasks.notifications",
    "app.tasks.reports",
    "app.tasks.cleanup",
]

# Auto-configure on first use
_celery_configured = False


@celery_app.on_after_configure.connect
def setup_configuration(**kwargs):
    """Setup configuration after Celery is configured."""
    global _celery_configured
    if not _celery_configured:
        configure_celery()
        _celery_configured = True
