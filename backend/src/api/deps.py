"""FastAPI dependency providers wiring sessions to services."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.core.storage import LocalFileStorage, get_storage
from src.repositories import AlertRepository, FileRepository
from src.services.alerts import AlertService
from src.services.files import FileService


SessionDep = Annotated[AsyncSession, Depends(get_session)]
StorageDep = Annotated[LocalFileStorage, Depends(get_storage)]


def get_file_service(session: SessionDep, storage: StorageDep) -> FileService:
    return FileService(FileRepository(session), storage)


def get_alert_service(session: SessionDep) -> AlertService:
    return AlertService(AlertRepository(session))


FileServiceDep = Annotated[FileService, Depends(get_file_service)]
AlertServiceDep = Annotated[AlertService, Depends(get_alert_service)]
