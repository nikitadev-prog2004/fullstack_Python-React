"""Alerts HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.deps import AlertServiceDep
from src.schemas import AlertItem

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[AlertItem])
async def list_alerts(service: AlertServiceDep) -> list[AlertItem]:
    alerts = await service.list_all()
    return [AlertItem.model_validate(item) for item in alerts]
