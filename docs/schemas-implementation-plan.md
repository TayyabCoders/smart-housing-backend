# Schemas Implementation Plan

**Goal:** Implement all Pydantic schemas for Smart Housing Surveillance system following the existing codebase conventions.

**Folder:** `app/schemas/`

---

## 1. Prerequisites

- Review existing schema patterns (`user_schema.py`, `auth_schema.py`)
- Follow Pydantic v2 conventions (`model_config = ConfigDict(from_attributes=True)`)
- Use proper typing (Optional, List, etc.)
- Import enums from `app.models.enums`
- Match frontend mock data shapes exactly

---

## 2. Implementation Order

### Step 1: Shared Base Schemas

**1.1 Pagination Schema (`app/schemas/common_schema.py`)**
- `PaginatedResponse[T]` with `items`, `total`, `limit`, `offset`
- Generic type using TypeVar
- Used across all list endpoints

**1.2 BBox Schema**
- `BBox` with `x`, `y`, `width`, `height` (for detection bounding boxes)

### Step 2: Dashboard Schema

**2.1 Dashboard Stats (`app/schemas/dashboard_schema.py`)**
```python
class DashboardStatsResponse(BaseModel):
    vehicles_today: int
    vehicles_yesterday_delta: int
    faces_verified: int
    faces_match_rate: float
    active_visitors: int
    visitors_awaiting_approval: int
    alerts_24h: int
    alerts_blacklist_count: int
```

### Step 3: Vehicle Detection Schemas

**3.1 Vehicle Detection Response (`app/schemas/vehicle_detection_schema.py`)**
```python
class MatchedVehicleInfo(BaseModel):
    owner_name: Optional[str]
    flat_no: Optional[str]
    vehicle_type: Optional[str]
    color: Optional[str]
    status: str

class VehicleDetectionResponse(BaseModel):
    id: UUID
    plate_number: str
    confidence: float
    bbox: Optional[dict]
    status: str
    image_url: Optional[str]
    full_frame_url: Optional[str]
    matched_vehicle: Optional[MatchedVehicleInfo]
    camera_name: Optional[str]
    detected_at: datetime
```

**3.2 Vehicle Detection Action Request**
```python
class VehicleDetectionActionRequest(BaseModel):
    action: Literal["open_gate", "block", "mark_visitor"]
```

**3.3 Vehicle Detection List Response**
- Extends `PaginatedResponse[VehicleDetectionResponse]`
- Add optional stats field

### Step 4: Face Detection Schemas

**4.1 Face Detection Response (`app/schemas/face_detection_schema.py`)**
```python
class MatchedPersonInfo(BaseModel):
    name: Optional[str]
    flat_no: Optional[str]
    role: str

class FaceDetectionResponse(BaseModel):
    id: UUID
    matched_person_id: Optional[UUID]
    confidence: float
    bbox: Optional[dict]
    status: str
    image_url: Optional[str]
    full_frame_url: Optional[str]
    matched_person: Optional[MatchedPersonInfo]
    camera_name: Optional[str]
    detected_at: datetime
```

**4.2 Face Detection Action Request**
```python
class FaceDetectionActionRequest(BaseModel):
    action: Literal["open_gate", "block", "allow", "deny", "flag_unknown", "register_visitor"]
```

**4.3 Face Detection List Response**
- Extends `PaginatedResponse[FaceDetectionResponse]`
- Add optional stats field

### Step 5: Alert Schemas

**5.1 Alert Response (`app/schemas/alert_schema.py`)**
```python
class AlertVehicleDetectionInfo(BaseModel):
    plate: Optional[str]
    status: Optional[str]

class AlertFaceDetectionInfo(BaseModel):
    person_name: Optional[str]
    status: Optional[str]

class AlertResponse(BaseModel):
    id: UUID
    kind: str
    severity: str
    title: str
    description: Optional[str]
    camera_name: Optional[str]
    vehicle_detection: Optional[AlertVehicleDetectionInfo]
    face_detection: Optional[AlertFaceDetectionInfo]
    status: str
    created_at: datetime
```

**5.2 Alert Action Requests**
```python
class AlertDismissRequest(BaseModel):
    pass  # Empty body, just ID in path

class AlertResolveRequest(BaseModel):
    pass  # Empty body, just ID in path
```

**5.3 Alert List Response**
- Extends `PaginatedResponse[AlertResponse]`

### Step 6: Person/Enrollment Schemas

**6.1 Person Response (`app/schemas/person_schema.py`)**
```python
class PersonResponse(BaseModel):
    id: UUID
    name: str
    role: str
    flat_no: Optional[str]
    phone: Optional[str]
    photo_url: Optional[str]
    is_active: bool
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    embeddings_count: int
    created_at: datetime
```

**6.2 Person Create Request**
```python
class PersonCreateRequest(BaseModel):
    name: str
    role: str
    flat_no: Optional[str]
    phone: Optional[str]
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
```

**6.3 Person Update Request**
- All fields optional except id

**6.4 Person Photo Upload Request**
```python
class PersonPhotoUploadRequest(BaseModel):
    photo: UploadFile  # FastAPI UploadFile
```

### Step 7: Vehicle Schemas

**7.1 Vehicle Response (`app/schemas/vehicle_schema.py`)**
```python
class VehicleResponse(BaseModel):
    id: UUID
    plate_number: str
    owner_id: Optional[UUID]
    owner_name: Optional[str]
    flat_no: Optional[str]
    vehicle_type: Optional[str]
    color: Optional[str]
    status: str
    notes: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
```

**7.2 Vehicle Create Request**
```python
class VehicleCreateRequest(BaseModel):
    plate_number: str
    owner_name: Optional[str]
    flat_no: Optional[str]
    vehicle_type: Optional[str]
    color: Optional[str]
    status: str
    notes: Optional[str]
```

**7.3 Vehicle Update Request**
- All fields optional except id

### Step 8: Camera Schemas

**8.1 Camera Response (`app/schemas/camera_schema.py`)**
```python
class CameraResponse(BaseModel):
    id: UUID
    code: str
    name: str
    location: Optional[str]
    stream_url: Optional[str]
    type: str
    is_active: bool
    created_at: datetime
```

**8.2 Camera Create Request**
```python
class CameraCreateRequest(BaseModel):
    code: str
    name: str
    location: Optional[str]
    stream_url: Optional[str]
    type: str
    is_active: bool = True
```

**8.3 Camera Update Request**
- All fields optional except id

---

## 3. Schema Conventions

### 3.1 Base Configuration
All response schemas should include:
```python
model_config = ConfigDict(from_attributes=True)
```

### 3.2 Field Types
- Use `UUID` from `uuid` module for ID fields
- Use `datetime` for timestamps
- Use `Optional[T]` for nullable fields
- Use `Literal` for enum-like string constraints
- Use proper enum types from `app.models.enums` where applicable

### 3.3 Naming Conventions
- Request schemas: `{Resource}CreateRequest`, `{Resource}UpdateRequest`, `{Resource}ActionRequest`
- Response schemas: `{Resource}Response`
- Nested info schemas: `{Context}{Resource}Info` (e.g., `MatchedVehicleInfo`)

### 3.4 Validation
- Add field validators where needed (email, phone format, etc.)
- Use `Field()` for constraints (min_length, max_length, etc.)
- Add description fields for API documentation

---

## 4. Files to Create

```
app/schemas/
├── __init__.py (update exports)
├── common_schema.py (new - pagination, bbox)
├── dashboard_schema.py (new)
├── vehicle_detection_schema.py (new)
├── face_detection_schema.py (new)
├── alert_schema.py (new)
├── person_schema.py (new)
├── vehicle_schema.py (new)
└── camera_schema.py (new)
```

---

## 5. Dependencies

Ensure `requirements.txt` includes:
- `pydantic>=2.0.0`
- `python-multipart` (for file uploads)

---

## 6. Testing

### 6.1 Schema Validation Tests
- Test required field validation
- Test optional field handling
- Test enum value validation
- Test datetime serialization

### 6.2 Integration Tests
- Test schema serialization from SQLAlchemy models
- Test request schema validation
- Test response schema serialization

---

## 7. Next Steps After Schemas

Once schemas are implemented:
1. Create/update repositories if needed
2. Implement services layer (inference, storage, detection services)
3. Create mediators for each domain
4. Implement HTTP routes using these schemas

---

**This plan focuses solely on the Pydantic schemas layer implementation. Once complete, move to HTTP routes.**
