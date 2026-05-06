"""Celery application instance."""

from __future__ import annotations

from celery import Celery

from src.core.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "file_tasks",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
    include=["src.tasks.pipeline"],
)

app = celery_app
