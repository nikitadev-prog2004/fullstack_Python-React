"""Data-access layer for alerts."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Alert


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Sequence[Alert]:
        result = await self._session.execute(
            select(Alert).order_by(Alert.created_at.desc())
        )
        return result.scalars().all()

    async def add(self, alert: Alert) -> None:
        self._session.add(alert)
