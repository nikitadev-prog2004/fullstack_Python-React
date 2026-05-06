"""End-to-end file processing pipeline.

The original codebase split processing into three Celery tasks
(scan -> metadata -> alert) chained via ``.delay()``. Each step opened
its own DB session, re-fetched the same row and committed it back, plus
each transition went through Redis. Since the steps run strictly
sequentially on the same row and there is no parallelism to gain, that
decomposition was pure overhead.

Here the pipeline runs as one unit of work:

* one DB session,
* one ``SELECT`` of the row,
* one ``UPDATE`` (or two when an alert row is added),
* zero extra Redis hops between phases.

The phases themselves remain split across small services
(``ThreatScanner``, ``MetadataExtractor``, ``AlertService``) so each piece
of business logic is still independently testable.
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.storage import LocalFileStorage
from src.models import ProcessingStatus, ScanStatus, StoredFile
from src.repositories import AlertRepository, FileRepository
from src.services.alerts import AlertService
from src.services.metadata import MetadataExtractor
from src.services.scanner import ThreatScanner

logger = logging.getLogger(__name__)


class ProcessingPipeline:
    def __init__(
        self,
        session: AsyncSession,
        storage: LocalFileStorage,
        scanner: ThreatScanner,
        extractor: MetadataExtractor,
        alert_service: AlertService,
    ) -> None:
        self._session = session
        self._storage = storage
        self._scanner = scanner
        self._extractor = extractor
        self._alert_service = alert_service

    async def run(self, file_id: str) -> None:
        repo = FileRepository(self._session)
        file_item = await repo.get(file_id)
        if file_item is None:
            logger.warning("ProcessingPipeline: file_id=%s not found", file_id)
            return

        try:
            self._apply_scan(file_item)
            self._apply_metadata(file_item)
        except Exception:
            logger.exception("ProcessingPipeline failed for file_id=%s", file_id)
            file_item.processing_status = ProcessingStatus.FAILED
            file_item.scan_status = file_item.scan_status or ScanStatus.FAILED
            file_item.scan_details = "processing failed"

        await self._alert_service.emit_for_file(file_item)
        await self._session.commit()

    def _apply_scan(self, file_item: StoredFile) -> None:
        verdict = self._scanner.scan(file_item)
        file_item.scan_status = verdict.status
        file_item.scan_details = verdict.details
        file_item.requires_attention = verdict.requires_attention

    def _apply_metadata(self, file_item: StoredFile) -> None:
        if not self._storage.exists(file_item.stored_name):
            file_item.processing_status = ProcessingStatus.FAILED
            file_item.scan_status = file_item.scan_status or ScanStatus.FAILED
            file_item.scan_details = "stored file not found during metadata extraction"
            return

        file_item.metadata_json = self._extractor.extract(file_item)
        file_item.processing_status = ProcessingStatus.PROCESSED


def build_pipeline(session: AsyncSession, storage: LocalFileStorage) -> ProcessingPipeline:
    return ProcessingPipeline(
        session=session,
        storage=storage,
        scanner=ThreatScanner(),
        extractor=MetadataExtractor(storage),
        alert_service=AlertService(AlertRepository(session)),
    )
