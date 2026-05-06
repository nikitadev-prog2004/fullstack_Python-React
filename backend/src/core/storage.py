"""Local filesystem storage for uploaded files."""

from __future__ import annotations

from pathlib import Path
from typing import BinaryIO

from fastapi import UploadFile

from src.core.config import get_settings


class LocalFileStorage:
    """Persists uploaded files on the local filesystem.

    The class abstracts the actual storage backend so the rest of the app
    does not depend on filesystem details. Replacing this with S3/MinIO
    later only touches this module.
    """

    def __init__(self, root: Path, chunk_size: int) -> None:
        self._root = root
        self._chunk_size = chunk_size
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        return self._root

    def path_for(self, stored_name: str) -> Path:
        return self._root / stored_name

    def exists(self, stored_name: str) -> bool:
        return self.path_for(stored_name).exists()

    def delete(self, stored_name: str) -> None:
        path = self.path_for(stored_name)
        if path.exists():
            path.unlink()

    async def save(self, stored_name: str, upload_file: UploadFile) -> int:
        """Stream upload to disk and return total bytes written."""
        path = self.path_for(stored_name)
        size = 0
        with path.open("wb") as out:
            while chunk := await upload_file.read(self._chunk_size):
                out.write(chunk)
                size += len(chunk)
        return size

    def open_binary(self, stored_name: str) -> BinaryIO:
        return self.path_for(stored_name).open("rb")


def get_storage() -> LocalFileStorage:
    settings = get_settings()
    return LocalFileStorage(
        root=settings.storage_dir,
        chunk_size=settings.upload_chunk_size,
    )
