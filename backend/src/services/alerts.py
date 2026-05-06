"""Alert authoring + listing service."""

from __future__ import annotations

from collections.abc import Sequence

from src.models import Alert, AlertLevel, ProcessingStatus, StoredFile
from src.repositories import AlertRepository


class AlertService:
    def __init__(self, repository: AlertRepository) -> None:
        self._repository = repository

    async def list_all(self) -> Sequence[Alert]:
        return await self._repository.list_all()

    async def emit_for_file(self, file_item: StoredFile) -> Alert:
        alert = self._build_alert(file_item)
        await self._repository.add(alert)
        return alert

    @staticmethod
    def _build_alert(file_item: StoredFile) -> Alert:
        if file_item.processing_status == ProcessingStatus.FAILED:
            return Alert(
                file_id=file_item.id,
                level=AlertLevel.CRITICAL,
                message="File processing failed",
            )
        if file_item.requires_attention:
            return Alert(
                file_id=file_item.id,
                level=AlertLevel.WARNING,
                message=f"File requires attention: {file_item.scan_details}",
            )
        return Alert(
            file_id=file_item.id,
            level=AlertLevel.INFO,
            message="File processed successfully",
        )
