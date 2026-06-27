# Smart Housing Surveillance Backend — Final Implementation Plan

**Goal:** Replace the frontend’s mock data with a fully functional backend, reusing the existing FastAPI + Mediator + DI + MQTT + Prometheus stack.

**Frontend:** `https://smart-entry-vision.lovable.app/`  
**Backend base:** existing FastAPI app with `auth_mediator.py`, `base_repository.py`, Mosquitto, Docker, and Alembic.

---

## 0. Architecture Decisions (Do First)

These decisions directly affect model design and deployment. The recommended defaults fit your current setup.

| Decision | Recommended choice | Reason |
|---|---|---|
| Object storage | **MinIO** (self-hosted via Docker) | Already running Docker; simple S3‑compatible API |
| ML inference | **In‑process worker** (load models at startup, async) | Low latency for single‑server; asyncio already in place |
| Gate trigger | **MQTT** (Mosquitto) | Reuse `Dockerfile.mqtt-publisher` and existing broker |
| Face embedding store | **pgvector** (PostgreSQL extension) | No new infrastructure; use existing Postgres |
| Camera ingestion | **RTSP pulled by backend** (OpenCV) | Centralised stream processing; swappable later |

---

## 1. Data Layer – Models & Migrations

**Folder:** `app/models/`

All models use UUID primary keys and UTC timestamps. Follow the existing `base_model.py` conventions.

### 1.1 Enums (`app/models/enums.py`)
```python
import enum

class CameraType(str, enum.Enum):
    PLATE = "plate"
    FACE = "face"
    BOTH = "both"

class VehicleStatus(str, enum.Enum):
    RESIDENT = "resident"
    VISITOR = "visitor"
    STAFF = "staff"
    BLACKLIST = "blacklist"

class DetectionStatus(str, enum.Enum):
    RESIDENT = "resident"
    VISITOR = "visitor"
    STAFF = "staff"
    BLACKLIST = "blacklist"
    UNKNOWN = "unknown"

class AlertKind(str, enum.Enum):
    BLACKLIST = "blacklist"
    UNKNOWN = "unknown"
    TAILGATE = "tailgate"
    EXPIRED = "expired"

class AlertSeverity(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class AlertStatus(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class ActionType(str, enum.Enum):
    OPEN_GATE = "open_gate"
    BLOCK = "block"
    MARK_VISITOR = "mark_visitor"
    ALLOW = "allow"
    DENY = "deny"
    FLAG_UNKNOWN = "flag_unknown"
    REGISTER_VISITOR = "register_visitor"   # Required by face unknown banner

class PersonRole(str, enum.Enum):
    RESIDENT = "resident"
    STAFF = "staff"
    VISITOR = "visitor"
```

### 1.2 Core Tables

**Camera**  
`id, code, name, location, stream_url, type(CameraType), is_active, created_at`

**Vehicle**  
`id, plate_number(unique), owner_id(FK→users, nullable), owner_name, flat_no, vehicle_type, color, status(VehicleStatus), notes, created_at, updated_at`

**VehicleDetection**  
`id, plate_number, matched_vehicle_id(FK→vehicles, nullable), confidence(Numeric), bbox(JSON), camera_id(FK), status(DetectionStatus), image_url, full_frame_url, action_taken(ActionType, nullable), acted_by(FK→users, nullable), detected_at`

**Person**  
`id, name, role(PersonRole), flat_no, phone, photo_url, is_active, valid_from, valid_until, created_at`

**FaceEmbedding** (pgvector)  
`id, person_id(FK→persons), vector(pgvector.VECTOR(512)), image_url, created_at`

**FaceDetection**  
`id, matched_person_id(FK→persons, nullable), confidence, bbox(JSON), camera_id(FK), status(DetectionStatus), image_url, full_frame_url, action_taken(ActionType, nullable), acted_by(FK→users, nullable), detected_at`

**Alert**  
`id, kind(AlertKind), severity(AlertSeverity), title, description, camera_id(FK), vehicle_detection_id(FK nullable), face_detection_id(FK nullable), status(AlertStatus, default=OPEN), resolved_by(FK, nullable), resolved_at, created_at`

**VisitorApproval** (new – essential for the “awaiting approval” workflow)  
`id, face_detection_id(FK), person_id(FK nullable), status(pending|approved|denied), created_at, decided_at`

### 1.3 Migrations
1. `alembic revision --autogenerate -m "surveillance core tables"`
2. Enable pgvector if not already: `op.execute("CREATE EXTENSION IF NOT EXISTS vector")`
3. Optional seed script for demo cameras/persons.

---

## 2. Repositories

**Folder:** `app/repositories/`  
Extend `base_repository.py` with the following.

| Repository | Key methods |
|---|---|
| `camera_repository` | `get_by_code(code)`, `list_active()` |
| `vehicle_repository` | `get_by_plate(plate)`, `list(filters, search, pagination)` |
| `vehicle_detection_repository` | `list(camera_id, status, date_from, date_to, search, offset, limit) -> (items, total)`, `stats(date_from) -> dict` |
| `person_repository` | `list(search, role, pagination)`, `get_active_visitors()` |
| `face_embedding_repository` | `get_all_active_embeddings() -> List[Tuple[UUID, np.array]]`, `get_by_person(person_id)` |
| `face_detection_repository` | Same pattern as vehicle detection + `stats()` |
| `alert_repository` | `list_open(kind, severity, pagination)`, `unread_count()`, `resolve(alert_id, user_id)`, `dismiss(alert_id)` |
| `visitor_approval_repository` | `list_pending()`, `approve(approval_id)`, `deny(approval_id)` |

All list methods return `(items, total)`.

---

## 3. Services

**Folder:** `app/services/`

### 3.1 `inference_service.py`
- Wraps ML models (YOLO, OCR, ArcFace/FaceNet). Loaded once at startup via DI.
- `detect_plate(image_bytes) -> dict` (plate_number, confidence, bbox)
- `detect_faces(image_bytes) -> list[dict]` (bbox, confidence, embedding vector)
- Allows swapping to a separate worker service later.

### 3.2 `storage_service.py`
- `upload_image(file_bytes, path_key) -> url`
- Uses MinIO client from new `app/configs/storage_config.py`.

### 3.3 `vehicle_detection_service.py`
- **detect()**: inference → plate match → determine status → save detection → create alert if blacklist → upload crop → return DTO.
- **apply_action()**: update detection record, MQTT gate command (for open_gate), handle `mark_visitor`.

### 3.4 `face_detection_service.py`
- **detect()**: inference → nearest‑neighbour match (pgvector or in‑memory index) → threshold decision → persist → alert if unknown/blacklist.
- **Action**: `register_visitor` creates a `VisitorApproval` entry.
- **Enroll person**: generate and store embeddings from multiple photos.

### 3.5 `camera_service.py`
- CRUD, MJPEG stream generator (OpenCV), health check.

### 3.6 `alert_service.py`
- `resolve()`, `dismiss()`, `list()`, `unread_count()`.

### 3.7 `gate_service.py`
- `publish_open(camera_id)` → MQTT message to `gate/{camera_id}/open`.

---

## 4. Mediators

**Folder:** `app/mediator/`

Following `auth_mediator.py`, each mediator composes services/repos and shapes response DTOs exactly as the frontend expects.

Example snippet (`vehicle_detection_mediator.py`):
```python
class VehicleDetectionMediator:
    def __init__(self, detection_service, vehicle_repo):
        ...

    async def handle_detect(self, file, camera_id, user_id):
        return await self.detection_service.detect(file, camera_id)

    async def list_detections(self, ...):
        items, total = self.detection_repo.list(...)
        stats = self.detection_repo.stats(...)
        return {"items": items, "total": total, "stats": stats}
```

---

## 5. Pydantic Schemas

**Folder:** `app/schemas/`

Define request/response models matching the frontend’s mock data shapes.

### 5.1 Dashboard (key endpoint)
```json
{
  "vehicles_today": 24,
  "vehicles_yesterday_delta": 8,
  "faces_verified": 156,
  "faces_match_rate": 97.4,
  "active_visitors": 3,
  "visitors_awaiting_approval": 2,
  "alerts_24h": 5,
  "alerts_blacklist_count": 1
}
```
`dashboard_schema.py` with `DashboardStatsResponse`.

### 5.2 Vehicle Detection
Response includes: `id, plate_number, confidence, bbox, status, image_url, matched_vehicle: {owner_name, flat_no, vehicle_type, color, status}`, `camera_name`, `detected_at`.
Action request: `{ action: "open_gate" | "block" | "mark_visitor" }`.

### 5.3 Face Detection
Similar, with `matched_person: {name, flat_no, role}` when known.
Action enum includes `register_visitor` (frontend’s unknown‑person banner).

### 5.4 Alerts
`{ id, kind, severity, title, description, camera_name, vehicle_detection? (plate, status), face_detection? (person name, status), status, created_at }`.

### 5.5 Persons (enrollment)
`PersonResponse`: `id, name, role, flat_no, phone, photo_url, is_active, valid_until, embeddings_count`.

### 5.6 Shared base
`PaginatedResponse[T]` with `items, total, limit, offset`.

---

## 6. HTTP Routes – Build Order

**Folder:** `app/edge/http/routes/` + controllers `app/edge/http/controller/`

Each phase is independently demoable against the frontend (swap mock‑data calls to real API).

### Phase A: MVP – Detection & Dashboard (Week 1)
1. `POST /api/vehicles/detect`
2. `POST /api/faces/detect`
3. `GET /api/dashboard/stats`

### Phase B: History & Actions (Week 2)
4. `GET /api/vehicles/detections` (filters, pagination)
5. `GET /api/faces/detections`
6. `POST /api/vehicles/detections/{id}/action`
7. `POST /api/faces/detections/{id}/action` (includes `register_visitor`)

### Phase C: Alerts (Week 2)
8. `GET /api/alerts`
9. `POST /api/alerts/{id}/dismiss`
10. `POST /api/alerts/{id}/resolve` (maps to “Review” button auto‑resolve)

### Phase D: Management CRUD (Week 3)
11. Vehicles: `GET/POST /api/vehicles`, `PATCH/DELETE /{id}`
12. Persons: `GET/POST /api/faces/persons`, `PATCH/DELETE /{id}`, `POST /{id}/photos`
13. Cameras: `GET/POST /api/cameras`, `PATCH/DELETE /{id}`

### Phase E: Live Stream (Week 3–4)
14. `GET /api/cameras/{id}/stream` (MJPEG proxy)

---

## 7. Real‑time WebSocket

**Endpoint:** `WS /ws/surveillance?camera_id=&token=`

Reuse your existing `connection_manager.py`. When a detection or alert is created, the service pushes:
```json
{
  "type": "vehicle_detection",
  "data": { ... }  // same shape as REST response
}
```
Broadcast `camera_status` events from a background health checker.

---

## 8. ML Worker (In‑Process)

**New file:** `app/infrastructure/ml_worker.py`

Load models at startup (YOLO vehicle/face, OCR, ArcFace). Expose async methods that run in a threadpool so the event loop isn’t blocked.

Register in DI:
```python
container.register_instance(MLWorker(), MLWorker)
```

`inference_service.py` then calls `await ml_worker.detect_plate(image_bytes)`.

---

## 9. Storage & Gate Integration

- **Storage config:** `app/configs/storage_config.py` – MinIO endpoint, credentials, bucket.
- **Storage service:** `storage_service.py` – upload via `boto3`, return URL.
- **Gate service:** `gate_service.py` – MQTT publisher to `gate/{camera_id}/command` with `{"action": "open"}`.

---

## 10. Testing & Hardening

- All routes protected by existing `auth_middleware` (except WebSocket which uses token query param).
- Custom `AppError(code, message)` + exception handler returning `{detail: message, code: "BLACKLIST_HIT"}`.
- Unit tests: mock repositories/services for mediator logic.
- Integration tests: `TestClient` against test DB, full flow from upload to action.

---

## 11. Build Order Summary

1. **Phase 0** – Decisions, MinIO, pgvector installation.
2. **Phases 1–4** – Models, repos, services, mediators (vehicles first, then faces).
3. **Phase A** – Detection endpoints + dashboard stats → **first live demo**.
4. **Phase 8** – Real ML models wired in.
5. **Phase B** – History, actions, alert generation.
6. **Phase C** – Alert management.
7. **Phase D** – CRUD management.
8. **Phase E + real‑time** – Live streams + WebSockets.
9. **Phase 10** – Testing, error handling, finalisation.

---

## 12. Quick Start: Dashboard Endpoint Example

```python
# app/mediator/dashboard_mediator.py
from datetime import datetime, timedelta
from app.schemas.dashboard_schema import DashboardStatsResponse

class DashboardMediator:
    def __init__(self, vehicle_repo, face_repo, alert_repo, visitor_approval_repo):
        ...

    async def get_stats(self):
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_start

        vehicles_today = vehicle_repo.count_since(today_start)
        vehicles_yesterday = vehicle_repo.count_between(yesterday_start, yesterday_end)
        delta = vehicles_today - vehicles_yesterday

        faces = face_repo.count_since(today_start)
        matched = face_repo.count_matched_since(today_start)
        match_rate = round((matched / faces) * 100, 1) if faces else 0

        visitors_awaiting = visitor_approval_repo.count_pending()
        active_visitors = face_repo.count_visitors()

        alerts_24h = alert_repo.count_since(now - timedelta(hours=24))
        blacklist_alerts = alert_repo.count_since_with_kind(now - timedelta(hours=24), "blacklist")

        return DashboardStatsResponse(
            vehicles_today=vehicles_today,
            vehicles_yesterday_delta=delta,
            faces_verified=matched,
            faces_match_rate=match_rate,
            active_visitors=active_visitors,
            visitors_awaiting_approval=visitors_awaiting,
            alerts_24h=alerts_24h,
            alerts_blacklist_count=blacklist_alerts
        )
```

**Route wiring:**
```python
@router.get("/api/dashboard/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(mediator: DashboardMediator = Depends()):
    return await mediator.get_stats()
```

---

**This plan is now fully aligned with the live frontend, your existing codebase, and the Phase 2 architecture decisions. You can start coding immediately.**
