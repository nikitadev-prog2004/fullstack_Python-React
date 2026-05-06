"""High-level file operations exposed to the HTTP layer."""

from __future__ import annotations

import mimetypes
from collections.abc import Sequence
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from src.core.storage import LocalFileStorage
from src.models import ProcessingStatus, StoredFile
from src.repositories import FileRepository


class FileService:
    def __init__(self, repository: FileRepository, storage: LocalFileStorage) -> None:
        self._repository = repository
        self._storage = storage

    async def list_all(self) -> Sequence[StoredFile]:
        return await self._repository.list_all()

    async def get(self, file_id: str) -> StoredFile:
        file_item = await self._repository.get(file_id)
        if file_item is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
            )
        return file_item

    async def get_with_path(self, file_id: str) -> tuple[StoredFile, Path]:
        file_item = await self.get(file_id)
        path = self._storage.path_for(file_item.stored_name)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found"
            )
        return file_item, path

    async def create(self, title: str, upload_file: UploadFile) -> StoredFile:
        file_id = str(uuid4())
        suffix = Path(upload_file.filename or "").suffix
        stored_name = f"{file_id}{suffix}"

        size = await self._storage.save(stored_name, upload_file)
        if size == 0:
            self._storage.delete(stored_name)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty"
            )

        mime_type = (
            upload_file.content_type
            or mimetypes.guess_type(stored_name)[0]
            or "application/octet-stream"
        )

        file_item = StoredFile(
            id=file_id,
            title=title,
            original_name=upload_file.filename or stored_name,
            stored_name=stored_name,
            mime_type=mime_type,
            size=size,
            processing_status=ProcessingStatus.UPLOADED,
        )
        await self._repository.add(file_item)
        return file_item

    async def update_title(self, file_id: str, title: str) -> StoredFile:
        file_item = await self.get(file_id)
        file_item.title = title
        return file_item

    async def delete(self, file_id: str) -> None:
        file_item = await self.get(file_id)
        self._storage.delete(file_item.stored_name)
        await self._repository.delete(file_item)
