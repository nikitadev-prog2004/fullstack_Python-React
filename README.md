## Тестовое задание на позицию Fullstack разработчика (Python + React)

**Запуск:**

```powershell
docker compose -f docker-compose.dev.yml down
docker compose -f docker-compose.dev.yml up --build
docker exec -it backend alembic upgrade head
```

**Открыть фронт:** `http://localhost:3000/test`

**Открыть бэк:** `http://localhost:8000/docs`

---

# Что было сделано

## 1. Backend: рефакторинг архитектуры

Монолит из 4 файлов (`app.py` + `service.py` + `tasks.py` + `models.py` + `schemas.py`) разрезан на слои:

```
backend/src/
├── core/         config, database, storage
├── models/       ORM (StoredFile, Alert) + статусы
├── schemas/      Pydantic DTO
├── repositories/ доступ к БД
├── services/     бизнес-логика (FileService, ThreatScanner, MetadataExtractor, AlertService, ProcessingPipeline)
├── api/          deps.py (DI) + routes/ (тонкие хендлеры)
├── tasks/        celery_app + одна задача process_file
└── app.py        FastAPI factory
```

- Routes — только HTTP-склейка.
- Services не знают про FastAPI/Celery.
- Repositories — единственное место с SQL.
- Бизнес-логика и контракты HTTP сохранены 1:1.

## 2. Backend: неочевидная оптимизация

Цепочка из трёх Celery-задач `scan → metadata → alert` свёрнута в одну `process_file`. На один файл вместо 3 сессий БД / 3 SELECT / 3 UPDATE / 2 хопов через Redis между фазами — **1 сессия / 1 SELECT / 1 UPDATE / 0 хопов**. Сервисы (`ThreatScanner`, `MetadataExtractor`, `AlertService`) остаются изолированными.

**Бонусом:** стриминг загрузки на диск (64 КБ чанки), потоковое чтение текста и PDF-маркеров, явный commit перед `delay()` (фикс гонки видимости строки в воркере), `download_file` больше не лезет в `STORAGE_DIR` напрямую.

## 3. Frontend: разбиение на слои

`page.tsx` (367 строк) → FSD-подобная структура:

```
frontend/src/
├── shared/    config, api/client (fetch+ApiError), hooks, lib/format
├── entities/  file/ и alert/ (types, api, hooks, ui/)
├── features/  upload-file/ (api, hooks, UploadFileModal)
├── widgets/   PageHeader, FilesTable, AlertsTable
└── app/       page.tsx (~50 строк, только композиция)
```

## 4. Фиксы запуска

- **`UploadFileModal.tsx`** — `next build` падал на TS-ошибке (Next.js 16 не сужал discriminated union в `else`). Перешёл на try/catch — короче и не зависит от strict-mode.
- **`frontend/.env.production`** — пустой плейсхолдер, чтобы стартовый `Dockerfile` (`COPY --from=builder /app/.env.production`) не валился.
- **`migrations/env.py`** — обновлён под новый путь к `Base` и `database_url`.
