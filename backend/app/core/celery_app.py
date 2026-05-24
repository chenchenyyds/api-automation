from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "api_automation",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_always_eager=False,
    beat_schedule={
        "daily-api-usage-report": {
            "task": "app.tasks.daily_report.send_daily_usage_report",
            "schedule": crontab(hour=9, minute=0),
            "options": {"queue": "celery"},
        },
    },
)

celery_app.autodiscover_tasks(["app.tasks"])
