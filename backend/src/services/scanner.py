"""Threat scanning logic.

Pure domain logic: no DB, no I/O. Returns a verdict for a file record so
it can be re-used both online (during upload) and offline (worker).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.models import ScanStatus, StoredFile


SUSPICIOUS_EXTENSIONS = frozenset({".exe", ".bat", ".cmd", ".sh", ".js"})
PDF_ALLOWED_MIME_TYPES = frozenset({"application/pdf", "application/octet-stream"})
LARGE_FILE_THRESHOLD_BYTES = 10 * 1024 * 1024


@dataclass(frozen=True)
class ScanVerdict:
    status: str
    details: str
    requires_attention: bool


class ThreatScanner:
    def scan(self, file_item: StoredFile) -> ScanVerdict:
        reasons: list[str] = []
        extension = Path(file_item.original_name).suffix.lower()

        if extension in SUSPICIOUS_EXTENSIONS:
            reasons.append(f"suspicious extension {extension}")

        if file_item.size > LARGE_FILE_THRESHOLD_BYTES:
            reasons.append("file is larger than 10 MB")

        if extension == ".pdf" and file_item.mime_type not in PDF_ALLOWED_MIME_TYPES:
            reasons.append("pdf extension does not match mime type")

        if reasons:
            return ScanVerdict(
                status=ScanStatus.SUSPICIOUS,
                details=", ".join(reasons),
                requires_attention=True,
            )
        return ScanVerdict(
            status=ScanStatus.CLEAN,
            details="no threats found",
            requires_attention=False,
        )
