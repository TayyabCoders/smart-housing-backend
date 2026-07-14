# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application

```bash
# Development (auto-reload)
python -m app.main

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000

# With Docker (light infra — recommended for dev)
docker-compose -f docker-compose.light.yml up -d
```

### Database Migrations (Alembic)

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "describe_change"

# Apply migrations
alembic upgrade head

# Downgrade one step
alembic downgrade -1
```

### Testing

```bash
pytest                        # all tests with coverage
pytest tests/unit/            # unit tests only
pytest tests/integration/     # integration tests only
pytest -k "test_name"         # single test by name
pytest --cov=app --cov-report=html  # coverage report
```

### Linting / Formatting

```bash
black app/
isort app/
flake8 app/
```

### RAG Sub-module

```bash
cd models/rag
python scripts/ingest.py                          # ingest documents into Qdrant
uvicorn api:app --host 0.0.0.0 --port 8001 --reload  # launch O.T.T.O RAG API
```

### Facial Detection Sub-module

```bash
cd models/facial_detection
python main.py
```

## Architecture

### Layer Stack

```
Routes → Controllers → Mediators → Services → Repositories → Database/Cache
```

Every layer is auto-discovered and registered by the DI loader (`app/di/loader.py`) using file naming conventions:
- `*_repository.py` → `XxxRepository` class (singletons via `container.register`)
- `*_service.py` → `XxxService` class
- `*_mediator.py` → `XxxMediator` class
- `*_controller.py` → `XxxController` class (singleton)

Dependencies are resolved by name string (`container.resolve("user_service")`) not by type.

### Dependency Injection

`app/di/container.py` holds a global `Container` (from `dependency-injector`). `load_all_dependencies()` in `loader.py` runs at startup in this fixed order: infrastructure → configs → utils → models → validators → strategies → repositories → services → mediators → controllers → wire.

To add a new resource, create the class file with the right suffix and the loader picks it up automatically. Infrastructure (database, cache, rabbitmq, kafka, prometheus) is registered manually in `load_infrastructure()`.

Routes get dependencies via `Depends(Provide["dependency_name"])` with `@inject`. The container is wired to `app.edge.http.routes`, `app.edge.http.controller`, `app.mediator`, `app.services`, `app.repositories`, and `app.middlewares`.

### Database

`app/configs/database_config.py` manages async SQLAlchemy with master/replica routing:
- `get_session("write")` → master
- `get_session("read")` → replica (falls back to master if replica is unconfigured)

All models inherit from `app/models/base_model.py::Base`. Add new models to `app/models/__init__.py` so Alembic autogenerate picks them up (import side-effects populate `Base.metadata`).

`DB_AUTO_MIGRATE=True` in `.env` runs `create_all` on startup (dev convenience); use Alembic migrations for production.

### Authentication

JWT-based auth via `python-jose`. `app/middlewares/auth_middleware.py` exports:
- `get_current_user` — requires valid access token, raises 401 otherwise
- `require_role(*roles)` — factory for RBAC, returns a `Depends`-compatible callable
- `require_admin` — convenience for admin-only routes

Public routes are whitelisted in `PUBLIC_ROUTES` inside that file.

### WebSocket

`app/edge/socket/connection_manager.py` — singleton `manager` handles connections, rooms, and broadcasting. `socket_handler.py` dispatches typed messages (`ping`, `subscribe`, `unsubscribe`, `room_message`, `broadcast`). WebSocket routes are registered separately after HTTP routes in `main.py`.

### Sub-modules

- **`models/rag/`** — standalone FastAPI + Qdrant RAG service ("O.T.T.O") for Smart Society knowledge base, exposed on port 8001 (`POST /chat`, `GET /health`) and proxied by the main backend's `app/services/chatbot_service.py` at `/api/v1/chatbot`. Has its own `.venv` and `requirements.txt`. Uses Groq (llama-3.1-8b-instant) as the LLM and BAAI/bge-small-en-v1.5 embeddings via fastembed.
- **`models/facial_detection/`** — standalone face recognition module with its own `.venv` and images directory.

Both sub-modules are independent Python projects; activate their own virtual environments when working on them.

### Key Config Variables

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | JWT signing (required) |
| `DB_AUTO_MIGRATE` | `True` runs `create_all` on startup |
| `DEBUG` | Enables `/docs`, `/redoc`, auto-reload |
| `REDIS_CLUSTER_MODE` | Toggle Redis cluster vs single-node |
| `PROMETHEUS_ENABLED` | Enable metrics endpoint |
| `CLOUDINARY_*` | Image upload credentials (required) |

Copy `env.example` to `.env` and fill in `SECRET_KEY`, `CLOUDINARY_*`, and DB credentials before running.

### Service Port Map (Docker)

| Service | External Port |
|---|---|
| FastAPI | 8000 |
| PostgreSQL master | 5433 |
| PostgreSQL replica | 5434 |
| Redis | 7004 |
| RabbitMQ | 5673 |
| RabbitMQ Mgmt | 15673 |
| Kafka | 9093 |
| Prometheus | 9091 |
| Grafana | 3002 |
