# Routes Implementation Plan

**Goal:** Implement all HTTP routes for Smart Housing Surveillance system following the existing codebase conventions.

**Folder:** `app/edge/http/routes/` + controllers `app/edge/http/controller/`

---

## 1. Prerequisites

- Review existing route patterns (`users_route.py`, `auth_route.py`)
- Follow FastAPI router conventions
- Use dependency injection for mediators/services
- Apply existing auth middleware for protection
- Use Pydantic schemas from Step 5

---

## 2. Implementation Order (Phased Approach)

Each phase is independently demoable against the frontend.

### Phase A: MVP – Detection & Dashboard (Week 1)

**2.1 Dashboard Stats Route**
- **File:** `app/edge/http/routes/dashboard_route.py`
- **Endpoint:** `GET /api/dashboard/stats`
- **Response:** `DashboardStatsResponse`
- **Dependencies:** `DashboardMediator`
- **Auth:** Required

**2.2 Vehicle Detection Route**
- **File:** `app/edge/http/routes/vehicle_detection_route.py`
- **Endpoint:** `POST /api/vehicles/detect`
- **Request:** `UploadFile` (image)
- **Query params:** `camera_id: UUID`
- **Response:** `VehicleDetectionResponse`
- **Dependencies:** `VehicleDetectionMediator`
- **Auth:** Required

**2.3 Face Detection Route**
- **File:** `app/edge/http/routes/face_detection_route.py`
- **Endpoint:** `POST /api/faces/detect`
- **Request:** `UploadFile` (image)
- **Query params:** `camera_id: UUID`
- **Response:** `FaceDetectionResponse`
- **Dependencies:** `FaceDetectionMediator`
- **Auth:** Required

### Phase B: History & Actions (Week 2)

**2.4 Vehicle Detection List Route**
- **File:** `app/edge/http/routes/vehicle_detection_route.py` (add to existing)
- **Endpoint:** `GET /api/vehicles/detections`
- **Query params:** `camera_id`, `status`, `date_from`, `date_to`, `search`, `offset`, `limit`
- **Response:** `PaginatedResponse[VehicleDetectionResponse]` with stats
- **Dependencies:** `VehicleDetectionMediator`
- **Auth:** Required

**2.5 Face Detection List Route**
- **File:** `app/edge/http/routes/face_detection_route.py` (add to existing)
- **Endpoint:** `GET /api/faces/detections`
- **Query params:** `camera_id`, `status`, `date_from`, `date_to`, `search`, `offset`, `limit`
- **Response:** `PaginatedResponse[FaceDetectionResponse]` with stats
- **Dependencies:** `FaceDetectionMediator`
- **Auth:** Required

**2.6 Vehicle Detection Action Route**
- **File:** `app/edge/http/routes/vehicle_detection_route.py` (add to existing)
- **Endpoint:** `POST /api/vehicles/detections/{id}/action`
- **Request:** `VehicleDetectionActionRequest`
- **Response:** Success message
- **Dependencies:** `VehicleDetectionMediator`
- **Auth:** Required

**2.7 Face Detection Action Route**
- **File:** `app/edge/http/routes/face_detection_route.py` (add to existing)
- **Endpoint:** `POST /api/faces/detections/{id}/action`
- **Request:** `FaceDetectionActionRequest`
- **Response:** Success message
- **Dependencies:** `FaceDetectionMediator`
- **Auth:** Required

### Phase C: Alerts (Week 2)

**2.8 Alerts List Route**
- **File:** `app/edge/http/routes/alert_route.py`
- **Endpoint:** `GET /api/alerts`
- **Query params:** `kind`, `severity`, `status`, `offset`, `limit`
- **Response:** `PaginatedResponse[AlertResponse]`
- **Dependencies:** `AlertMediator`
- **Auth:** Required

**2.9 Alert Dismiss Route**
- **File:** `app/edge/http/routes/alert_route.py` (add to existing)
- **Endpoint:** `POST /api/alerts/{id}/dismiss`
- **Response:** Success message
- **Dependencies:** `AlertMediator`
- **Auth:** Required

**2.10 Alert Resolve Route**
- **File:** `app/edge/http/routes/alert_route.py` (add to existing)
- **Endpoint:** `POST /api/alerts/{id}/resolve`
- **Response:** Success message
- **Dependencies:** `AlertMediator`
- **Auth:** Required

### Phase D: Management CRUD (Week 3)

**2.11 Vehicles CRUD Routes**
- **File:** `app/edge/http/routes/vehicle_route.py`
- **Endpoints:**
  - `GET /api/vehicles` (list with filters, pagination)
  - `POST /api/vehicles` (create)
  - `GET /api/vehicles/{id}` (get by id)
  - `PATCH /api/vehicles/{id}` (update)
  - `DELETE /api/vehicles/{id}` (delete)
- **Dependencies:** `VehicleMediator`
- **Auth:** Required

**2.12 Persons CRUD Routes**
- **File:** `app/edge/http/routes/person_route.py`
- **Endpoints:**
  - `GET /api/faces/persons` (list with filters, pagination)
  - `POST /api/faces/persons` (create)
  - `GET /api/faces/persons/{id}` (get by id)
  - `PATCH /api/faces/persons/{id}` (update)
  - `DELETE /api/faces/persons/{id}` (delete)
  - `POST /api/faces/persons/{id}/photos` (upload photo for enrollment)
- **Dependencies:** `PersonMediator`
- **Auth:** Required

**2.13 Cameras CRUD Routes**
- **File:** `app/edge/http/routes/camera_route.py`
- **Endpoints:**
  - `GET /api/cameras` (list)
  - `POST /api/cameras` (create)
  - `GET /api/cameras/{id}` (get by id)
  - `PATCH /api/cameras/{id}` (update)
  - `DELETE /api/cameras/{id}` (delete)
- **Dependencies:** `CameraMediator`
- **Auth:** Required

### Phase E: Live Stream (Week 3–4)

**2.14 Camera Stream Route**
- **File:** `app/edge/http/routes/camera_route.py` (add to existing)
- **Endpoint:** `GET /api/cameras/{id}/stream`
- **Response:** MJPEG stream (StreamingResponse)
- **Dependencies:** `CameraMediator`, `CameraService`
- **Auth:** Required

---

## 3. Route Conventions

### 3.1 Router Setup
```python
from fastapi import APIRouter, Depends, UploadFile, File, Query
from typing import Optional

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])
```

### 3.2 Dependency Injection Pattern
```python
from app.di.container import get_container
from app.mediator.vehicle_detection_mediator import VehicleDetectionMediator

def get_vehicle_detection_mediator() -> VehicleDetectionMediator:
    container = get_container()
    return container.resolve(VehicleDetectionMediator)

@router.post("/detect")
async def detect_vehicle(
    file: UploadFile = File(...),
    camera_id: UUID = Query(...),
    mediator: VehicleDetectionMediator = Depends(get_vehicle_detection_mediator)
):
    return await mediator.handle_detect(file, camera_id)
```

### 3.3 Error Handling
- Use existing `AppError` exception class
- Return proper HTTP status codes (200, 201, 400, 404, 500)
- Include error details in response

### 3.4 File Upload Handling
- Use `UploadFile` from FastAPI
- Validate file types (image/jpeg, image/png)
- Add file size limits
- Pass file bytes to services

### 3.5 Query Parameter Validation
- Use Pydantic models for complex query params
- Add default values for pagination (offset=0, limit=20)
- Validate date formats (ISO 8601)

### 3.6 Response Models
- Use `response_model` parameter in route decorators
- Ensure all responses match schema definitions
- Include proper status codes

---

## 4. Controller Pattern (Optional)

If using controller pattern (like `auth_controller.py`):
- Route files delegate to controller methods
- Controllers contain business logic coordination
- Controllers use mediators/services

**Example:**
```python
# app/edge/http/controller/vehicle_detection_controller.py
class VehicleDetectionController:
    def __init__(self, mediator: VehicleDetectionMediator):
        self.mediator = mediator
    
    async def detect(self, file: UploadFile, camera_id: UUID):
        return await self.mediator.handle_detect(file, camera_id)

# Route file
@router.post("/detect")
async def detect_vehicle(
    file: UploadFile = File(...),
    camera_id: UUID = Query(...),
    controller: VehicleDetectionController = Depends(get_vehicle_detection_controller)
):
    return await controller.detect(file, camera_id)
```

---

## 5. Route Registration

**File:** `app/main.py` (or `app/edge/http/routes/__init__.py`)

Register all routers in the main FastAPI app:
```python
from app.edge.http.routes.dashboard_route import router as dashboard_router
from app.edge.http.routes.vehicle_detection_route import router as vehicle_detection_router
from app.edge.http.routes.face_detection_route import router as face_detection_router
from app.edge.http.routes.alert_route import router as alert_router
from app.edge.http.routes.vehicle_route import router as vehicle_router
from app.edge.http.routes.person_route import router as person_router
from app.edge.http.routes.camera_route import router as camera_router

app.include_router(dashboard_router)
app.include_router(vehicle_detection_router)
app.include_router(face_detection_router)
app.include_router(alert_router)
app.include_router(vehicle_router)
app.include_router(person_router)
app.include_router(camera_router)
```

---

## 6. Files to Create

```
app/edge/http/routes/
├── __init__.py (update exports)
├── dashboard_route.py (new)
├── vehicle_detection_route.py (new)
├── face_detection_route.py (new)
├── alert_route.py (new)
├── vehicle_route.py (new)
├── person_route.py (new)
└── camera_route.py (new)

app/edge/http/controller/ (optional)
├── __init__.py
├── dashboard_controller.py (new)
├── vehicle_detection_controller.py (new)
├── face_detection_controller.py (new)
├── alert_controller.py (new)
├── vehicle_controller.py (new)
├── person_controller.py (new)
└── camera_controller.py (new)
```

---

## 7. Dependencies

Ensure `requirements.txt` includes:
- `fastapi>=0.104.0`
- `python-multipart` (for file uploads)

---

## 8. Testing

### 8.1 Route Tests
- Test each endpoint with valid requests
- Test authentication/authorization
- Test error handling (invalid inputs, missing resources)
- Test file upload validation

### 8.2 Integration Tests
- Use `TestClient` from FastAPI
- Test full request-response cycle
- Test mediator/service integration
- Test database operations

---

## 9. API Documentation

FastAPI automatically generates OpenAPI docs at:
- `/docs` (Swagger UI)
- `/redoc` (ReDoc)

Ensure:
- All routes have proper tags
- Request/response models are documented
- Query parameters have descriptions
- Error responses are documented

---

## 10. Next Steps After Routes

Once routes are implemented:
1. Implement mediators for each domain
2. Implement services (inference, storage, detection)
3. Implement/update repositories
4. Wire up dependency injection
5. Test end-to-end with frontend

---

**This plan focuses solely on the HTTP routes layer implementation. Once complete, integrate with mediators and services.**
