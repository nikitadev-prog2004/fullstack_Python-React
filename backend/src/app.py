"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import alerts as alerts_routes
from src.api.routes import files as files_routes
from src.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="File exchange MVP")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_allow_origins),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(files_routes.router)
    app.include_router(alerts_routes.router)
    return app


app = create_app()
