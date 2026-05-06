"""Celery tasks. The whole post-upload pipeline runs as one task."""

from __future__ import annotations

import asyncio
import logging

from src.core.database import get_session_factory
from src.core.storage import get_storage
from src.services.processing import build_pipeline
from src.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

_worker_loop: asyncio.AbstractEventLoop | None = None


def _run(coro):
    """Run an async coroutine on a per-worker event loop.

    Celery workers are sync; we keep one event loop for the worker
    process so async resources (engine, connection pools) survive
    across tasks.
    """
    global _worker_loop
    if _worker_loop is None or _worker_loop.is_closed():
        _worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_worker_loop)
    return _worker_loop.run_until_complete(coro)


async def _process(file_id: str) -> None:
    session_factory = get_session_factory()
    storage = get_storage()
    async with session_factory() as session:
        pipeline = build_pipeline(session, storage)
        await pipeline.run(file_id)


@celery_app.task(name="files.process")
def process_file(file_id: str) -> None:
    """Scan, extract metadata and emit alert in a single transaction."""
    _run(_process(file_id))
