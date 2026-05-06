"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class Settings:
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    celery_broker_url: str
    celery_result_backend: str

    storage_dir: Path
    upload_chunk_size: int

    cors_allow_origins: tuple[str, ...]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


def _env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable {name!r} is required")
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    broker_url = os.environ.get("CELERY_BROKER_URL") or os.environ.get(
        "REDIS_URL", "redis://backend-redis:6379/0"
    )
    result_backend = os.environ.get("CELERY_RESULT_BACKEND", broker_url)

    return Settings(
        postgres_user=_env("POSTGRES_USER"),
        postgres_password=_env("POSTGRES_PASSWORD"),
        postgres_host=_env("POSTGRES_HOST"),
        postgres_port=_env("PGPORT", "5432"),
        postgres_db=_env("POSTGRES_DB"),
        celery_broker_url=broker_url,
        celery_result_backend=result_backend,
        storage_dir=BASE_DIR / "storage" / "files",
        upload_chunk_size=64 * 1024,
        cors_allow_origins=(
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ),
    )
