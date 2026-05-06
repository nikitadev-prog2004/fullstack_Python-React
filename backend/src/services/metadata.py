"""Metadata extraction.

The original implementation read the entire file into memory in order to
count lines / locate PDF page markers. We stream the file instead so the
worker stays bounded in memory regardless of file size.
"""

from __future__ import annotations

from pathlib import Path

from src.core.storage import LocalFileStorage
from src.models import StoredFile


_TEXT_CHUNK = 64 * 1024
_BIN_CHUNK = 256 * 1024
_PAGE_MARKER = b"/Type /Page"


class MetadataExtractor:
    def __init__(self, storage: LocalFileStorage) -> None:
        self._storage = storage

    def extract(self, file_item: StoredFile) -> dict[str, object]:
        metadata: dict[str, object] = {
            "extension": Path(file_item.original_name).suffix.lower(),
            "size_bytes": file_item.size,
            "mime_type": file_item.mime_type,
        }

        if file_item.mime_type.startswith("text/"):
            metadata.update(self._text_metadata(file_item.stored_name))
        elif file_item.mime_type == "application/pdf":
            metadata["approx_page_count"] = self._pdf_page_count(file_item.stored_name)

        return metadata

    def _text_metadata(self, stored_name: str) -> dict[str, int]:
        line_count = 0
        char_count = 0
        path = self._storage.path_for(stored_name)
        with path.open("r", encoding="utf-8", errors="ignore") as fh:
            while chunk := fh.read(_TEXT_CHUNK):
                char_count += len(chunk)
                line_count += chunk.count("\n")
        return {"line_count": line_count, "char_count": char_count}

    def _pdf_page_count(self, stored_name: str) -> int:
        count = 0
        tail = b""
        path = self._storage.path_for(stored_name)
        marker_len = len(_PAGE_MARKER)
        with path.open("rb") as fh:
            while chunk := fh.read(_BIN_CHUNK):
                buf = tail + chunk
                count += buf.count(_PAGE_MARKER)
                tail = buf[-(marker_len - 1):] if marker_len > 1 else b""
        return max(count, 1)
