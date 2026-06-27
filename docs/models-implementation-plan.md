# Models Implementation Plan

**Goal:** Implement all data models for Smart Housing Surveillance system following the existing codebase conventions.

**Folder:** `app/models/`

---

## 1. Prerequisites

- Check existing `base_model.py` for conventions (UUID primary keys, UTC timestamps)
- Ensure SQLAlchemy 2.0+ syntax is used
- All models use async/await pattern
- Follow existing repository pattern from `base_repository.py`

---

## 2. Implementation Order

### Step 1: Enums (`app/models/enums.py`)
Create all enum classes first as they are dependencies for other models.

**Enums to implement:**
- `CameraType` (plate, face, both)
- `VehicleStatus` (resident, visitor, staff, blacklist)
- `DetectionStatus` (resident, visitor, staff, blacklist, unknown)
- `AlertKind` (blacklist, unknown, tailgate, expired)
- `AlertSeverity` (high, medium, low)
- `AlertStatus` (open, resolved, dismissed)
- `ActionType` (open_gate, block, mark_visitor, allow, deny, flag_unknown, register_visitor)
- `PersonRole` (resident, staff, visitor)

### Step 2: Core Models

**2.1 Camera Model**
- Fields: id, code, name, location, stream_url, type, is_active, created_at
- Relationships: One-to-many with VehicleDetection and FaceDetection

**2.2 Vehicle Model**
- Fields: id, plate_number (unique), owner_id (FK→users, nullable), owner_name, flat_no, vehicle_type, color, status, notes, created_at, updated_at
- Relationships: One-to-many with VehicleDetection

**2.3 VehicleDetection Model**
- Fields: id, plate_number, matched_vehicle_id (FK→vehicles, nullable), confidence, bbox (JSON), camera_id (FK), status, image_url, full_frame_url, action_taken (nullable), acted_by (FK→users, nullable), detected_at
- Relationships: Belongs to Camera, Vehicle (optional), User (acted_by)

**2.4 Person Model**
- Fields: id, name, role, flat_no, phone, photo_url, is_active, valid_from, valid_until, created_at
- Relationships: One-to-many with FaceEmbedding, FaceDetection

**2.5 FaceEmbedding Model** (pgvector)
- Fields: id, person_id (FK→persons), vector (pgvector.VECTOR(512)), image_url, created_at
- Dependencies: Requires pgvector extension in PostgreSQL
- Relationships: Belongs to Person

**2.6 FaceDetection Model**
- Fields: id, matched_person_id (FK→persons, nullable), confidence, bbox (JSON), camera_id (FK), status, image_url, full_frame_url, action_taken (nullable), acted_by (FK→users, nullable), detected_at
- Relationships: Belongs to Camera, Person (optional), User (acted_by)

**2.7 Alert Model**
- Fields: id, kind, severity, title, description, camera_id (FK), vehicle_detection_id (FK nullable), face_detection_id (FK nullable), status (default=OPEN), resolved_by (FK, nullable), resolved_at, created_at
- Relationships: Belongs to Camera, VehicleDetection (optional), FaceDetection (optional), User (resolved_by)

**2.8 VisitorApproval Model**
- Fields: id, face_detection_id (FK), person_id (FK nullable), status (pending|approved|denied), created_at, decided_at
- Relationships: Belongs to FaceDetection, Person (optional)

---

## 3. Model Conventions

### 3.1 Base Model
All models should inherit from existing `BaseModel` with:
- UUID primary key (`id`)
- `created_at` timestamp (UTC, default=now)
- `updated_at` timestamp (UTC, default=now, onupdate=now) where applicable

### 3.2 Field Types
- Use SQLAlchemy 2.0 syntax (`Mapped[T]`, `mapped_column`)
- UUID fields: `UUID` type
- Timestamps: `DateTime(timezone=True)` with UTC
- JSON fields: `JSON` type for bbox, metadata
- Numeric: `Numeric(precision, scale)` for confidence scores
- Foreign keys: `ForeignKey` with proper relationships

### 3.3 Relationships
- Use `relationship()` with proper back_populates
- Define lazy loading strategy (selectin, joined, or raise)
- Cascade delete where appropriate

### 3.4 Indexes
- Add indexes on frequently queried fields:
  - Vehicle: plate_number (unique)
  - Detections: camera_id, detected_at, status
  - Alerts: status, created_at, kind
  - VisitorApproval: status, created_at

---

## 4. Database Migration

### 4.1 Enable pgvector Extension
In the migration file, add:
```python
op.execute("CREATE EXTENSION IF NOT EXISTS vector")
```

### 4.2 Migration Steps
1. Run `alembic revision --autogenerate -m "surveillance core tables"`
2. Review generated migration
3. Add pgvector extension creation
4. Run `alembic upgrade head`

### 4.3 Verification
- Check all tables created in database
- Verify pgvector extension is installed
- Test foreign key constraints
- Validate indexes

---

## 5. Testing

### 5.1 Model Validation Tests
- Test enum values
- Test required field constraints
- Test unique constraints
- Test foreign key relationships

### 5.2 Integration Tests
- Test model creation via SQLAlchemy
- Test relationship loading
- Test cascade operations

---

## 6. Next Steps After Models

Once models are implemented and migrated:
1. Create repositories for each model
2. Implement Pydantic schemas for API
3. Build services layer
4. Create mediators
5. Implement HTTP routes

---

## 7. Files to Create

```
app/models/
├── __init__.py
├── base_model.py (existing - review)
├── enums.py (new)
├── camera.py (new)
├── vehicle.py (new)
├── vehicle_detection.py (new)
├── person.py (new)
├── face_embedding.py (new)
├── face_detection.py (new)
├── alert.py (new)
└── visitor_approval.py (new)
```

---

## 8. Dependencies

Ensure `requirements.txt` includes:
- `sqlalchemy>=2.0.23`
- `asyncpg>=0.29.0` (PostgreSQL async driver)
- `pgvector` (Python package for pgvector support)

---

**This plan focuses solely on the data layer implementation. Once complete, move to repositories and services.**
