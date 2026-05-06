"""Data-access layer for stored files."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import StoredFile


class FileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[StoredFile]:
        result = await self._session.execute(
            select(StoredFile).order_by(StoredFile.created_at.desc())
        )
        return result.scalars().all()

    async def get(self, file_id: str) -> StoredFile | None:
        return await self._session.get(StoredFile, file_id)

    async def add(self, file_item: StoredFile) -> None:
        self._session.add(file_item)

    async def delete(self, file_item: StoredFile) -> None:
        await self._session.delete(file_item)
