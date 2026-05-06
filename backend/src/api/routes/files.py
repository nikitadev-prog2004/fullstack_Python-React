"""Files HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import FileResponse

from src.api.deps import FileServiceDep, SessionDep
from src.schemas import FileItem, FileUpdate
from src.tasks.pipeline import process_file

router = APIRouter(prefix="/files", tags=["files"])


@router.get("", response_model=list[FileItem])
async def list_files(service: FileServiceDep) -> list[FileItem]:
    files = await service.list_all()
    return [FileItem.model_validate(item) for item in files]


@router.post("", response_model=FileItem, status_code=201)
async def create_file(
    service: FileServiceDep,
    session: SessionDep,
    title: str = Form(...),
    file: UploadFile = File(...),
) -> FileItem:
    file_item = await service.create(title=title, upload_file=file)
    # Commit before scheduling the worker so the row is visible to it.
    await session.commit()
    process_file.delay(file_item.id)
    return FileItem.model_validate(file_item)


@router.get("/{file_id}", response_model=FileItem)
async def get_file(file_id: str, service: FileServiceDep) -> FileItem:
    file_item = await service.get(file_id)
    return FileItem.model_validate(file_item)


@router.patch("/{file_id}", response_model=FileItem)
async def update_file(
    file_id: str,
    payload: FileUpdate,
    service: FileServiceDep,
) -> FileItem:
    file_item = await service.update_title(file_id=file_id, title=payload.title)
    return FileItem.model_validate(file_item)


@router.get("/{file_id}/download")
async def download_file(file_id: str, service: FileServiceDep) -> FileResponse:
    file_item, path = await service.get_with_path(file_id)
    return FileResponse(
        path=path,
        media_type=file_item.mime_type,
        filename=file_item.original_name,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file(file_id: str, service: FileServiceDep) -> None:
    await service.delete(file_id)
