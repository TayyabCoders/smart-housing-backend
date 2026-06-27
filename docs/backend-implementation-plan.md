# Smart Surveillance Backend - Detailed Implementation Plan

Comprehensive detailed implementation plan for AI-powered vehicle plate and facial recognition backend system supporting the Lovable frontend at https://smart-entry-vision.lovable.app/.

---

# Table of Contents

1. [Database Schema & Models](#1-database-schema--models)
2. [Pydantic Schemas](#2-pydantic-schemas)
3. [Repository Layer](#3-repository-layer)
4. [Service Layer](#4-service-layer)
5. [Controller Layer](#5-controller-layer)
6. [API Routes](#6-api-routes)
7. [WebSocket Implementation](#7-websocket-implementation)
8. [AI Integration](#8-ai-integration)
9. [Configuration](#9-configuration)
10. [Utilities](#10-utilities)
11. [Middleware](#11-middleware)
12. [Testing Strategy](#12-testing-strategy)

---

# 1. Database Schema & Models

## 1.1 User Model

**File**: `app/models/user_model.py`

```python
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.models.base_model import BaseModel
import uuid
import enum

class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

class User(BaseModel):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    username = Column(String(100), unique=True, index=True)
    password = Column(String(255), nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER)
    
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
```

**Migration**: `alembic/versions/001_create_users.py`

```python
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), unique=True),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('status', sa.Enum('pending', 'active', 'suspended', name='userstatus'), default='pending'),
        sa.Column('role', sa.Enum('admin', 'operator', 'viewer', name='userrole'), default='viewer'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_status', 'users', ['status'])
```

---

## 1.2 Camera Model

**File**: `app/models/camera_model.py`

```python
from sqlalchemy import Column, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.models.base_model import BaseModel
import uuid
import enum

class CameraType(str, enum.Enum):
    PLATE = "plate"
    FACE = "face"
    BOTH = "both"

class Camera(BaseModel):
    __tablename__ = "cameras"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255))
    stream_url = Column(String(500))
    type = Column(SQLEnum(CameraType), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    
    created_at = Column(DateTime, nullable=False)
```

**Migration**: `alembic/versions/002_create_cameras.py`

```python
def upgrade():
    op.create_table(
        'cameras',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('location', sa.String(255)),
        sa.Column('stream_url', sa.String(500)),
        sa.Column('type', sa.Enum('plate', 'face', 'both', name='cameratype'), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_cameras_code', 'cameras', ['code'])
    op.create_index('ix_cameras_is_active', 'cameras', ['is_active'])
```

---

## 1.3 Vehicle Model

**File**: `app/models/vehicle_model.py`

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import uuid
import enum

class VehicleStatus(str, enum.Enum):
    RESIDENT = "resident"
    VISITOR = "visitor"
    STAFF = "staff"
    BLACKLIST = "blacklist"

class Vehicle(BaseModel):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_number = Column(String(50), unique=True, nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    owner_name = Column(String(255), nullable=False)
    flat_no = Column(String(50))
    vehicle_type = Column(String(100))
    color = Column(String(50))
    status = Column(SQLEnum(VehicleStatus), default=VehicleStatus.RESIDENT, index=True)
    notes = Column(String(1000))
    
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    owner = relationship("User", backref="vehicles")
```

**Migration**: `alembic/versions/003_create_vehicles.py`

```python
def upgrade():
    op.create_table(
        'vehicles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('plate_number', sa.String(50), unique=True, nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('owner_name', sa.String(255), nullable=False),
        sa.Column('flat_no', sa.String(50)),
        sa.Column('vehicle_type', sa.String(100)),
        sa.Column('color', sa.String(50)),
        sa.Column('status', sa.Enum('resident', 'visitor', 'staff', 'blacklist', name='vehiclestatus'), default='resident'),
        sa.Column('notes', sa.String(1000)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_vehicles_plate_number', 'vehicles', ['plate_number'])
    op.create_index('ix_vehicles_status', 'vehicles', ['status'])
    op.create_foreign_key('fk_vehicles_owner_id', 'vehicles', 'users', ['owner_id'], ['id'])
```

---

## 1.4 Vehicle Detection Model

**File**: `app/models/vehicle_detection_model.py`

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import uuid
import enum

class DetectionStatus(str, enum.Enum):
    RESIDENT = "resident"
    VISITOR = "staff"
    STAFF = "staff"
    BLACKLIST = "blacklist"
    UNKNOWN = "unknown"

class DetectionSource(str, enum.Enum):
    LIVE_UPLOAD = "live_upload"
    BATCH_PROCESSING = "batch_processing"
    API = "api"

class DetectionAction(str, enum.Enum):
    OPEN_GATE = "open_gate"
    BLOCK = "block"
    MARK_VISITOR = "mark_visitor"
    NONE = "none"

class VehicleDetection(BaseModel):
    __tablename__ = "vehicle_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate_number = Column(String(50), index=True)
    matched_vehicle_id = Column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=True)
    status = Column(SQLEnum(DetectionStatus), index=True)
    confidence = Column(Numeric(5, 2))
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cameras.id'), nullable=True)
    
    image_url = Column(String(1000))
    full_frame_url = Column(String(1000))
    bbox = Column(JSON)
    
    source = Column(SQLEnum(DetectionSource), default=DetectionSource.LIVE_UPLOAD)
    
    action_taken = Column(SQLEnum(DetectionAction), default=DetectionAction.NONE)
    acted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    detected_at = Column(DateTime, nullable=False, index=True)

    matched_vehicle = relationship("Vehicle", backref="detections")
    camera = relationship("Camera", backref="vehicle_detections")
    actor = relationship("User", foreign_keys=[acted_by])
```

**Migration**: `alembic/versions/004_create_vehicle_detections.py`

```python
def upgrade():
    op.create_table(
        'vehicle_detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('plate_number', sa.String(50)),
        sa.Column('matched_vehicle_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicles.id')),
        sa.Column('status', sa.Enum('resident', 'visitor', 'staff', 'blacklist', 'unknown', name='detectionstatus')),
        sa.Column('confidence', sa.Numeric(5, 2)),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cameras.id')),
        sa.Column('image_url', sa.String(1000)),
        sa.Column('full_frame_url', sa.String(1000)),
        sa.Column('bbox', postgresql.JSON()),
        sa.Column('source', sa.Enum('live_upload', 'batch_processing', 'api', name='detectionsource')),
        sa.Column('action_taken', sa.Enum('open_gate', 'block', 'mark_visitor', 'none', name='detectionaction')),
        sa.Column('acted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_vehicle_detections_plate_number', 'vehicle_detections', ['plate_number'])
    op.create_index('ix_vehicle_detections_status', 'vehicle_detections', ['status'])
    op.create_index('ix_vehicle_detections_detected_at', 'vehicle_detections', ['detected_at'])
    op.create_index('ix_vehicle_detections_camera_detected_at', 'vehicle_detections', ['camera_id', 'detected_at'])
    op.create_foreign_key('fk_vehicle_detections_matched_vehicle_id', 'vehicle_detections', 'vehicles', ['matched_vehicle_id'], ['id'])
    op.create_foreign_key('fk_vehicle_detections_camera_id', 'vehicle_detections', 'cameras', ['camera_id'], ['id'])
    op.create_foreign_key('fk_vehicle_detections_acted_by', 'vehicle_detections', 'users', ['acted_by'], ['id'])
```

---

## 1.5 Person Model

**File**: `app/models/person_model.py`

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import uuid
import enum

class PersonRole(str, enum.Enum):
    RESIDENT = "resident"
    STAFF = "staff"
    VISITOR = "visitor"

class Person(BaseModel):
    __tablename__ = "persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    role = Column(SQLEnum(PersonRole), nullable=False, index=True)
    
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    flat_no = Column(String(50))
    phone = Column(String(20))
    
    photo_url = Column(String(1000))
    
    is_active = Column(Boolean, default=True, index=True)
    
    valid_from = Column(DateTime, nullable=True)
    valid_until = Column(DateTime, nullable=True, index=True)
    
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", backref="persons")
    face_embeddings = relationship("FaceEmbedding", back_populates="person", cascade="all, delete-orphan")
```

**Migration**: `alembic/versions/005_create_persons.py`

```python
def upgrade():
    op.create_table(
        'persons',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('resident', 'staff', 'visitor', name='personrole'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('flat_no', sa.String(50)),
        sa.Column('phone', sa.String(20)),
        sa.Column('photo_url', sa.String(1000)),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('valid_from', sa.DateTime()),
        sa.Column('valid_until', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_persons_role', 'persons', ['role'])
    op.create_index('ix_persons_is_active', 'persons', ['is_active'])
    op.create_index('ix_persons_valid_until', 'persons', ['valid_until'])
    op.create_foreign_key('fk_persons_user_id', 'persons', 'users', ['user_id'], ['id'])
```

---

## 1.6 Face Embedding Model

**File**: `app/models/face_embedding_model.py`

```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, TEXT
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import uuid

class FaceEmbedding(BaseModel):
    __tablename__ = "face_embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    person_id = Column(UUID(as_uuid=True), ForeignKey('persons.id'), nullable=False, index=True)
    
    embedding = Column(TEXT, nullable=False)  # JSON array as string
    image_url = Column(String(1000))
    
    created_at = Column(DateTime, nullable=False)

    person = relationship("Person", back_populates="face_embeddings")
```

**Migration**: `alembic/versions/006_create_face_embeddings.py`

```python
def upgrade():
    op.create_table(
        'face_embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('persons.id'), nullable=False),
        sa.Column('embedding', sa.TEXT(), nullable=False),
        sa.Column('image_url', sa.String(1000)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_face_embeddings_person_id', 'face_embeddings', ['person_id'])
    op.create_foreign_key('fk_face_embeddings_person_id', 'face_embeddings', 'persons', ['person_id'], ['id'])
```

---

## 1.7 Face Detection Model

**File**: `app/models/face_detection_model.py`

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSON, TEXT
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import uuid
import enum

class FaceDetectionStatus(str, enum.Enum):
    RESIDENT = "resident"
    STAFF = "staff"
    VISITOR = "visitor"
    BLACKLIST = "blacklist"
    UNKNOWN = "unknown"

class FaceDetectionAction(str, enum.Enum):
    ALLOW = "allow"
    DENY = "deny"
    FLAG_UNKNOWN = "flag_unknown"
    NONE = "none"

class FaceDetection(BaseModel):
    __tablename__ = "face_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matched_person_id = Column(UUID(as_uuid=True), ForeignKey('persons.id'), nullable=True)
    
    status = Column(SQLEnum(FaceDetectionStatus), index=True)
    confidence = Column(Numeric(5, 2))
    
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cameras.id'), nullable=True)
    
    image_url = Column(String(1000))
    full_frame_url = Column(String(1000))
    
    bbox = Column(JSON)
    embedding = Column(TEXT)
    
    source = Column(SQLEnum(DetectionSource), default=DetectionSource.LIVE_UPLOAD)
    
    action_taken = Column(SQLEnum(FaceDetectionAction), default=FaceDetectionAction.NONE)
    acted_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    
    detected_at = Column(DateTime, nullable=False, index=True)

    matched_person = relationship("Person", backref="face_detections")
    camera = relationship("Camera", backref="face_detections")
    actor = relationship("User", foreign_keys=[acted_by])
```

**Migration**: `alembic/versions/007_create_face_detections.py`

```python
def upgrade():
    op.create_table(
        'face_detections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('matched_person_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('persons.id')),
        sa.Column('status', sa.Enum('resident', 'staff', 'visitor', 'blacklist', 'unknown', name='facedetectionstatus')),
        sa.Column('confidence', sa.Numeric(5, 2)),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cameras.id')),
        sa.Column('image_url', sa.String(1000)),
        sa.Column('full_frame_url', sa.String(1000)),
        sa.Column('bbox', postgresql.JSON()),
        sa.Column('embedding', sa.TEXT()),
        sa.Column('source', sa.Enum('live_upload', 'batch_processing', 'api', name='detectionsource')),
        sa.Column('action_taken', sa.Enum('allow', 'deny', 'flag_unknown', 'none', name='facedetectionaction')),
        sa.Column('acted_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('detected_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_face_detections_status', 'face_detections', ['status'])
    op.create_index('ix_face_detections_detected_at', 'face_detections', ['detected_at'])
    op.create_index('ix_face_detections_camera_detected_at', 'face_detections', ['camera_id', 'detected_at'])
    op.create_foreign_key('fk_face_detections_matched_person_id', 'face_detections', 'persons', ['matched_person_id'], ['id'])
    op.create_foreign_key('fk_face_detections_camera_id', 'face_detections', 'cameras', ['camera_id'], ['id'])
    op.create_foreign_key('fk_face_detections_acted_by', 'face_detections', 'users', ['acted_by'], ['id'])
```

---

## 1.8 Alert Model

**File**: `app/models/alert_model.py`

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import uuid
import enum

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

class Alert(BaseModel):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kind = Column(SQLEnum(AlertKind), nullable=False, index=True)
    severity = Column(SQLEnum(AlertSeverity), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    description = Column(String(1000))
    
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cameras.id'), nullable=True)
    
    vehicle_detection_id = Column(UUID(as_uuid=True), ForeignKey('vehicle_detections.id'), nullable=True)
    face_detection_id = Column(UUID(as_uuid=True), ForeignKey('face_detections.id'), nullable=True)
    
    status = Column(SQLEnum(AlertStatus), default=AlertStatus.OPEN, index=True)
    
    resolved_by = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, nullable=False, index=True)

    camera = relationship("Camera", backref="alerts")
    vehicle_detection = relationship("VehicleDetection", backref="alerts")
    face_detection = relationship("FaceDetection", backref="alerts")
    resolver = relationship("User", foreign_keys=[resolved_by])
```

**Migration**: `alembic/versions/008_create_alerts.py`

```python
def upgrade():
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('kind', sa.Enum('blacklist', 'unknown', 'tailgate', 'expired', name='alertkind'), nullable=False),
        sa.Column('severity', sa.Enum('high', 'medium', 'low', name='alertseverity'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String(1000)),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cameras.id')),
        sa.Column('vehicle_detection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('vehicle_detections.id')),
        sa.Column('face_detection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('face_detections.id')),
        sa.Column('status', sa.Enum('open', 'resolved', 'dismissed', name='alertstatus'), default='open'),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id')),
        sa.Column('resolved_at', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_alerts_kind', 'alerts', ['kind'])
    op.create_index('ix_alerts_severity', 'alerts', ['severity'])
    op.create_index('ix_alerts_status', 'alerts', ['status'])
    op.create_index('ix_alerts_created_at', 'alerts', ['created_at'])
    op.create_foreign_key('fk_alerts_camera_id', 'alerts', 'cameras', ['camera_id'], ['id'])
    op.create_foreign_key('fk_alerts_vehicle_detection_id', 'alerts', 'vehicle_detections', ['vehicle_detection_id'], ['id'])
    op.create_foreign_key('fk_alerts_face_detection_id', 'alerts', 'face_detections', ['face_detection_id'], ['id'])
    op.create_foreign_key('fk_alerts_resolved_by', 'alerts', 'users', ['resolved_by'], ['id'])
```

---

## 1.9 Entry Log Model

**File**: `app/models/entry_log_model.py`

```python
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base_model import BaseModel
import uuid
import enum

class EntryLogType(str, enum.Enum):
    VEHICLE = "vehicle"
    FACE = "face"
    BOTH = "both"

class EntryLogStatus(str, enum.Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    PENDING = "pending"

class EntryLog(BaseModel):
    __tablename__ = "entry_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_type = Column(SQLEnum(EntryLogType), nullable=False, index=True)
    detection_id = Column(UUID(as_uuid=True), nullable=False)
    
    camera_id = Column(UUID(as_uuid=True), ForeignKey('cameras.id'), nullable=True)
    
    status = Column(SQLEnum(EntryLogStatus), default=EntryLogStatus.PENDING, index=True)
    action_taken = Column(String(100))
    
    created_at = Column(DateTime, nullable=False, index=True)

    camera = relationship("Camera", backref="entry_logs")
```

**Migration**: `alembic/versions/009_create_entry_logs.py`

```python
def upgrade():
    op.create_table(
        'entry_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('detection_type', sa.Enum('vehicle', 'face', 'both', name='entrylogtype'), nullable=False),
        sa.Column('detection_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('camera_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('cameras.id')),
        sa.Column('status', sa.Enum('allowed', 'denied', 'pending', name='entrylogstatus'), default='pending'),
        sa.Column('action_taken', sa.String(100)),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_entry_logs_detection_type', 'entry_logs', ['detection_type'])
    op.create_index('ix_entry_logs_status', 'entry_logs', ['status'])
    op.create_index('ix_entry_logs_created_at', 'entry_logs', ['created_at'])
    op.create_index('ix_entry_logs_camera_detected_at', 'entry_logs', ['camera_id', 'created_at'])
    op.create_foreign_key('fk_entry_logs_camera_id', 'entry_logs', 'cameras', ['camera_id'], ['id'])
```

---

# 2. Pydantic Schemas

## 2.1 User Schemas

**File**: `app/schemas/user_schema.py`

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"

class UserStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    SUSPENDED = "suspended"

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.VIEWER

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None

class UserResponse(UserBase):
    id: UUID
    status: UserStatus
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
```

---

## 2.2 Camera Schemas

**File**: `app/schemas/camera_schema.py`

```python
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

class CameraType(str, enum.Enum):
    PLATE = "plate"
    FACE = "face"
    BOTH = "both"

class CameraBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = None
    stream_url: Optional[HttpUrl] = None
    type: CameraType
    is_active: bool = True

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    stream_url: Optional[HttpUrl] = None
    type: Optional[CameraType] = None
    is_active: Optional[bool] = None

class CameraResponse(CameraBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class CameraStreamResponse(BaseModel):
    camera_id: UUID
    stream_url: str
    status: str
```

---

## 2.3 Vehicle Schemas

**File**: `app/schemas/vehicle_schema.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

class VehicleStatus(str, enum.Enum):
    RESIDENT = "resident"
    VISITOR = "visitor"
    STAFF = "staff"
    BLACKLIST = "blacklist"

class VehicleBase(BaseModel):
    plate_number: str = Field(..., min_length=5, max_length=20)
    owner_name: str = Field(..., min_length=1, max_length=255)
    flat_no: Optional[str] = None
    vehicle_type: Optional[str] = None
    color: Optional[str] = None
    status: VehicleStatus = VehicleStatus.RESIDENT
    notes: Optional[str] = None

class VehicleCreate(VehicleBase):
    owner_id: Optional[UUID] = None

class VehicleUpdate(BaseModel):
    owner_name: Optional[str] = None
    flat_no: Optional[str] = None
    vehicle_type: Optional[str] = None
    color: Optional[str] = None
    status: Optional[VehicleStatus] = None
    notes: Optional[str] = None

class VehicleResponse(VehicleBase):
    id: UUID
    owner_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]
    total: int
    limit: int
    offset: int
```

---

## 2.4 Vehicle Detection Schemas

**File**: `app/schemas/vehicle_detection_schema.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import enum

class DetectionStatus(str, enum.Enum):
    RESIDENT = "resident"
    VISITOR = "visitor"
    STAFF = "staff"
    BLACKLIST = "blacklist"
    UNKNOWN = "unknown"

class DetectionAction(str, enum.Enum):
    OPEN_GATE = "open_gate"
    BLOCK = "block"
    MARK_VISITOR = "mark_visitor"
    NONE = "none"

class VehicleDetectionCreate(BaseModel):
    file: bytes  # Multipart file upload
    camera_id: Optional[UUID] = None

class VehicleDetectionResponse(BaseModel):
    id: UUID
    plate_number: Optional[str]
    confidence: Optional[float]
    bbox: Optional[Dict[str, float]]
    matched_vehicle: Optional[VehicleResponse]
    status: DetectionStatus
    image_url: Optional[str]
    detected_at: datetime

    class Config:
        from_attributes = True

class VehicleDetectionActionRequest(BaseModel):
    action: DetectionAction
    note: Optional[str] = None

class VehicleDetectionActionResponse(BaseModel):
    ok: bool
    action_taken: DetectionAction
    acted_by: UUID

class VehicleDetectionListResponse(BaseModel):
    items: list[VehicleDetectionResponse]
    total: int
    limit: int
    offset: int
    stats: Dict[str, int]
```

---

## 2.5 Person Schemas

**File**: `app/schemas/person_schema.py`

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

class PersonRole(str, enum.Enum):
    RESIDENT = "resident"
    STAFF = "staff"
    VISITOR = "visitor"

class PersonBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    role: PersonRole
    flat_no: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

class PersonCreate(PersonBase):
    user_id: Optional[UUID] = None

class PersonUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[PersonRole] = None
    flat_no: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

class PersonResponse(PersonBase):
    id: UUID
    user_id: Optional[UUID]
    photo_url: Optional[str]
    embeddings_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class PersonEnrollRequest(BaseModel):
    name: str
    role: PersonRole
    flat_no: Optional[str] = None
    phone: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    photos: list[bytes]  # Multiple photos for embedding

class PersonListResponse(BaseModel):
    items: list[PersonResponse]
    total: int
    limit: int
    offset: int
```

---

## 2.6 Face Detection Schemas

**File**: `app/schemas/face_detection_schema.py`

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
import enum

class FaceDetectionStatus(str, enum.Enum):
    RESIDENT = "resident"
    STAFF = "staff"
    VISITOR = "visitor"
    BLACKLIST = "blacklist"
    UNKNOWN = "unknown"

class FaceDetectionAction(str, enum.Enum):
    ALLOW = "allow"
    DENY = "deny"
    FLAG_UNKNOWN = "flag_unknown"
    NONE = "none"

class FaceDetectionCreate(BaseModel):
    file: bytes  # Multipart file upload
    camera_id: Optional[UUID] = None

class FaceDetectionResponse(BaseModel):
    id: UUID
    confidence: Optional[float]
    bbox: Optional[Dict[str, float]]
    matched_person: Optional[PersonResponse]
    status: FaceDetectionStatus
    image_url: Optional[str]
    detected_at: datetime

    class Config:
        from_attributes = True

class FaceDetectionActionRequest(BaseModel):
    action: FaceDetectionAction
    note: Optional[str] = None

class FaceDetectionActionResponse(BaseModel):
    ok: bool
    action_taken: FaceDetectionAction
    acted_by: UUID

class FaceDetectionListResponse(BaseModel):
    items: list[FaceDetectionResponse]
    total: int
    limit: int
    offset: int
    stats: Dict[str, int]
```

---

## 2.7 Alert Schemas

**File**: `app/schemas/alert_schema.py`

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

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

class AlertBase(BaseModel):
    kind: AlertKind
    severity: AlertSeverity
    title: str
    description: Optional[str] = None

class AlertCreate(AlertBase):
    camera_id: Optional[UUID] = None
    vehicle_detection_id: Optional[UUID] = None
    face_detection_id: Optional[UUID] = None

class AlertResponse(AlertBase):
    id: UUID
    camera_id: Optional[UUID]
    camera_name: Optional[str]
    vehicle_detection_id: Optional[UUID]
    face_detection_id: Optional[UUID]
    status: AlertStatus
    resolved_by: Optional[UUID]
    resolved_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class AlertResolveRequest(BaseModel):
    note: Optional[str] = None

class AlertResolveResponse(BaseModel):
    ok: bool

class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int
    unread: int
    limit: int
    offset: int
```

---

## 2.8 Entry Log Schemas

**File**: `app/schemas/entry_log_schema.py`

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID
import enum

class EntryLogType(str, enum.Enum):
    VEHICLE = "vehicle"
    FACE = "face"
    BOTH = "both"

class EntryLogStatus(str, enum.Enum):
    ALLOWED = "allowed"
    DENIED = "denied"
    PENDING = "pending"

class EntryLogResponse(BaseModel):
    id: UUID
    detection_type: EntryLogType
    detection_id: UUID
    camera_id: Optional[UUID]
    camera_name: Optional[str]
    status: EntryLogStatus
    action_taken: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class EntryLogListResponse(BaseModel):
    items: list[EntryLogResponse]
    total: int
    limit: int
    offset: int
```

---

# 3. Repository Layer

## 3.1 Base Repository

**File**: `app/repositories/base_repository.py` (extend existing)

```python
from typing import TypeVar, Generic, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: UUID) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        search_fields: Optional[List[str]] = None
    ) -> tuple[List[ModelType], int]:
        query = self.db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        if search and search_fields:
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    search_conditions.append(getattr(self.model, field).ilike(f"%{search}%"))
            if search_conditions:
                query = query.filter(or_(*search_conditions))
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: UUID) -> ModelType:
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj

    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(getattr(self.model, field) == value).first()
```

---

## 3.2 User Repository

**File**: `app/repositories/user_repository.py`

```python
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.user_model import User, UserStatus
from app.schemas.user_schema import UserCreate, UserUpdate
from app.repositories.base_repository import BaseRepository

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_active_users(self, skip: int = 0, limit: int = 100) -> Tuple[List[User], int]:
        return self.get_multi(skip, limit, filters={"status": UserStatus.ACTIVE})

    def soft_delete(self, id: UUID) -> Optional[User]:
        user = self.get(id)
        if user:
            from datetime import datetime
            user.deleted_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user
```

---

## 3.3 Camera Repository

**File**: `app/repositories/camera_repository.py`

```python
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.camera_model import Camera, CameraType
from app.schemas.camera_schema import CameraCreate, CameraUpdate
from app.repositories.base_repository import BaseRepository

class CameraRepository(BaseRepository[Camera, CameraCreate, CameraUpdate]):
    def __init__(self, db: Session):
        super().__init__(Camera, db)

    def get_by_code(self, code: str) -> Optional[Camera]:
        return self.db.query(Camera).filter(Camera.code == code).first()

    def get_active_cameras(self) -> List[Camera]:
        return self.db.query(Camera).filter(Camera.is_active == True).all()

    def get_by_type(self, camera_type: CameraType) -> List[Camera]:
        return self.db.query(Camera).filter(Camera.type == camera_type).all()
```

---

## 3.4 Vehicle Repository

**File**: `app/repositories/vehicle_repository.py`

```python
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate
from app.repositories.base_repository import BaseRepository

class VehicleRepository(BaseRepository[Vehicle, VehicleCreate, VehicleUpdate]):
    def __init__(self, db: Session):
        super().__init__(Vehicle, db)

    def get_by_plate_number(self, plate_number: str) -> Optional[Vehicle]:
        return self.db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()

    def get_by_status(self, status: VehicleStatus, skip: int = 0, limit: int = 100) -> Tuple[List[Vehicle], int]:
        return self.get_multi(skip, limit, filters={"status": status}, search_fields=["plate_number", "owner_name"])

    def get_blacklisted_vehicles(self) -> List[Vehicle]:
        return self.db.query(Vehicle).filter(Vehicle.status == VehicleStatus.BLACKLIST).all()
```

---

## 3.5 Vehicle Detection Repository

**File**: `app/repositories/vehicle_detection_repository.py`

```python
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from uuid import UUID
from datetime import datetime
from app.models.vehicle_detection_model import VehicleDetection, DetectionStatus
from app.schemas.vehicle_detection_schema import VehicleDetectionCreate, VehicleDetectionUpdate
from app.repositories.base_repository import BaseRepository

class VehicleDetectionRepository(BaseRepository[VehicleDetection, VehicleDetectionCreate, VehicleDetectionUpdate]):
    def __init__(self, db: Session):
        super().__init__(VehicleDetection, db)

    def get_recent_detections(
        self,
        camera_id: Optional[UUID] = None,
        status: Optional[DetectionStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[VehicleDetection], int]:
        query = self.db.query(VehicleDetection)
        
        if camera_id:
            query = query.filter(VehicleDetection.camera_id == camera_id)
        
        if status:
            query = query.filter(VehicleDetection.status == status)
        
        if from_date:
            query = query.filter(VehicleDetection.detected_at >= from_date)
        
        if to_date:
            query = query.filter(VehicleDetection.detected_at <= to_date)
        
        if search:
            query = query.filter(VehicleDetection.plate_number.ilike(f"%{search}%"))
        
        query = query.order_by(desc(VehicleDetection.detected_at))
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_statistics(self, from_date: Optional[datetime] = None) -> Dict[str, int]:
        query = self.db.query(VehicleDetection)
        
        if from_date:
            query = query.filter(VehicleDetection.detected_at >= from_date)
        
        total = query.count()
        residents = query.filter(VehicleDetection.status == DetectionStatus.RESIDENT).count()
        visitors = query.filter(VehicleDetection.status == DetectionStatus.VISITOR).count()
        blacklist = query.filter(VehicleDetection.status == DetectionStatus.BLACKLIST).count()
        
        return {
            "total": total,
            "residents": residents,
            "visitors": visitors,
            "blacklist": blacklist
        }
```

---

## 3.6 Person Repository

**File**: `app/repositories/person_repository.py`

```python
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.person_model import Person, PersonRole
from app.schemas.person_schema import PersonCreate, PersonUpdate
from app.repositories.base_repository import BaseRepository

class PersonRepository(BaseRepository[Person, PersonCreate, PersonUpdate]):
    def __init__(self, db: Session):
        super().__init__(Person, db)

    def get_by_role(self, role: PersonRole, skip: int = 0, limit: int = 100) -> Tuple[List[Person], int]:
        return self.get_multi(skip, limit, filters={"role": role}, search_fields=["name", "flat_no"])

    def get_active_persons(self) -> List[Person]:
        return self.db.query(Person).filter(Person.is_active == True).all()

    def get_valid_persons(self) -> List[Person]:
        from datetime import datetime
        now = datetime.utcnow()
        return self.db.query(Person).filter(
            and_(
                Person.is_active == True,
                Person.valid_from <= now,
                (Person.valid_until >= now) | (Person.valid_until.is_(None))
            )
        ).all()
```

---

## 3.7 Face Embedding Repository

**File**: `app/repositories/face_embedding_repository.py`

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from UUID import UUID
from app.models.face_embedding_model import FaceEmbedding
from app.schemas.face_embedding_schema import FaceEmbeddingCreate, FaceEmbeddingUpdate
from app.repositories.base_repository import BaseRepository

class FaceEmbeddingRepository(BaseRepository[FaceEmbedding, FaceEmbeddingCreate, FaceEmbeddingUpdate]):
    def __init__(self, db: Session):
        super().__init__(FaceEmbedding, db)

    def get_by_person_id(self, person_id: UUID) -> List[FaceEmbedding]:
        return self.db.query(FaceEmbedding).filter(FaceEmbedding.person_id == person_id).all()

    def get_all_embeddings(self) -> List[FaceEmbedding]:
        return self.db.query(FaceEmbedding).all()
```

---

## 3.8 Face Detection Repository

**File**: `app/repositories/face_detection_repository.py`

```python
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from uuid import UUID
from datetime import datetime
from app.models.face_detection_model import FaceDetection, FaceDetectionStatus
from app.schemas.face_detection_schema import FaceDetectionCreate, FaceDetectionUpdate
from app.repositories.base_repository import BaseRepository

class FaceDetectionRepository(BaseRepository[FaceDetection, FaceDetectionCreate, FaceDetectionUpdate]):
    def __init__(self, db: Session):
        super().__init__(FaceDetection, db)

    def get_recent_detections(
        self,
        camera_id: Optional[UUID] = None,
        status: Optional[FaceDetectionStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[FaceDetection], int]:
        query = self.db.query(FaceDetection)
        
        if camera_id:
            query = query.filter(FaceDetection.camera_id == camera_id)
        
        if status:
            query = query.filter(FaceDetection.status == status)
        
        if from_date:
            query = query.filter(FaceDetection.detected_at >= from_date)
        
        if to_date:
            query = query.filter(FaceDetection.detected_at <= to_date)
        
        query = query.order_by(desc(FaceDetection.detected_at))
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total

    def get_statistics(self, from_date: Optional[datetime] = None) -> Dict[str, int]:
        query = self.db.query(FaceDetection)
        
        if from_date:
            query = query.filter(FaceDetection.detected_at >= from_date)
        
        total = query.count()
        residents = query.filter(FaceDetection.status == FaceDetectionStatus.RESIDENT).count()
        staff = query.filter(FaceDetection.status == FaceDetectionStatus.STAFF).count()
        visitors = query.filter(FaceDetection.status == FaceDetectionStatus.VISITOR).count()
        unknown = query.filter(FaceDetection.status == FaceDetectionStatus.UNKNOWN).count()
        
        return {
            "total": total,
            "residents": residents,
            "staff": staff,
            "visitors": visitors,
            "unknown": unknown
        }
```

---

## 3.9 Alert Repository

**File**: `app/repositories/alert_repository.py`

```python
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from uuid import UUID
from datetime import datetime
from app.models.alert_model import Alert, AlertKind, AlertSeverity, AlertStatus
from app.schemas.alert_schema import AlertCreate, AlertUpdate
from app.repositories.base_repository import BaseRepository

class AlertRepository(BaseRepository[Alert, AlertCreate, AlertUpdate]):
    def __init__(self, db: Session):
        super().__init__(Alert, db)

    def get_open_alerts(
        self,
        kind: Optional[AlertKind] = None,
        severity: Optional[AlertSeverity] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[Alert], int]:
        filters = {"status": AlertStatus.OPEN}
        if kind:
            filters["kind"] = kind
        if severity:
            filters["severity"] = severity
        
        return self.get_multi(skip, limit, filters=filters)

    def get_unread_count(self) -> int:
        return self.db.query(Alert).filter(Alert.status == AlertStatus.OPEN).count()

    def resolve_alert(self, alert_id: UUID, resolved_by: UUID) -> Optional[Alert]:
        alert = self.get(alert_id)
        if alert:
            alert.status = AlertStatus.RESOLVED
            alert.resolved_by = resolved_by
            alert.resolved_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(alert)
        return alert

    def dismiss_alert(self, alert_id: UUID) -> Optional[Alert]:
        alert = self.get(alert_id)
        if alert:
            alert.status = AlertStatus.DISMISSED
            self.db.commit()
            self.db.refresh(alert)
        return alert
```

---

## 3.10 Entry Log Repository

**File**: `app/repositories/entry_log_repository.py`

```python
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from uuid import UUID
from datetime import datetime
from app.models.entry_log_model import EntryLog, EntryLogType, EntryLogStatus
from app.schemas.entry_log_schema import EntryLogCreate, EntryLogUpdate
from app.repositories.base_repository import BaseRepository

class EntryLogRepository(BaseRepository[EntryLog, EntryLogCreate, EntryLogUpdate]):
    def __init__(self, db: Session):
        super().__init__(EntryLog, db)

    def get_logs(
        self,
        detection_type: Optional[EntryLogType] = None,
        camera_id: Optional[UUID] = None,
        status: Optional[EntryLogStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50
    ) -> Tuple[List[EntryLog], int]:
        query = self.db.query(EntryLog)
        
        if detection_type:
            query = query.filter(EntryLog.detection_type == detection_type)
        
        if camera_id:
            query = query.filter(EntryLog.camera_id == camera_id)
        
        if status:
            query = query.filter(EntryLog.status == status)
        
        if from_date:
            query = query.filter(EntryLog.created_at >= from_date)
        
        if to_date:
            query = query.filter(EntryLog.created_at <= to_date)
        
        query = query.order_by(desc(EntryLog.created_at))
        
        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total
```

---

# 4. Service Layer

## 4.1 Authentication Service

**File**: `app/services/auth_service.py` (extend existing)

```python
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from uuid import UUID
from app.models.user_model import User, UserStatus
from app.schemas.user_schema import UserCreate, UserLogin, TokenResponse
from app.repositories.user_repository import UserRepository

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_user(self, user_in: UserCreate) -> User:
        # Check if email exists
        if self.user_repo.get_by_email(user_in.email):
            raise ValueError("Email already registered")
        
        # Hash password
        user_data = user_in.model_dump()
        user_data["password"] = self.get_password_hash(user_data["password"])
        user_data["created_at"] = datetime.utcnow()
        user_data["updated_at"] = datetime.utcnow()
        
        return self.user_repo.create(UserCreate(**user_data))

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        user = self.user_repo.get_by_email(email)
        if not user:
            return None
        if not self.verify_password(password, user.password):
            return None
        if user.status != UserStatus.ACTIVE:
            raise ValueError("User account is not active")
        return user

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def login(self, credentials: UserLogin) -> TokenResponse:
        user = self.authenticate_user(credentials.email, credentials.password)
        if not user:
            raise ValueError("Invalid credentials")
        
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}
        access_token = self.create_access_token(token_data)
        refresh_token = self.create_refresh_token(token_data)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=user
        )
```

---

## 4.2 ALPR Service

**File**: `app/services/alpr_service.py`

```python
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import cv2
import numpy as np
from app.models.vehicle_detection_model import VehicleDetection, DetectionStatus, DetectionAction
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.vehicle_detection_repository import VehicleDetectionRepository
from app.utils.image_util import ImageUtil
from app.utils.storage_util import StorageUtil

class ALPRService:
    def __init__(self, db: Session):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)
        self.detection_repo = VehicleDetectionRepository(db)
        self.image_util = ImageUtil()
        self.storage_util = StorageUtil()

    def detect_plate(self, image_bytes: bytes, camera_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Detect license plate from image using YOLO + OCR
        Returns detection data with plate number, confidence, bbox
        """
        # TODO: Integrate YOLO + OCR models
        # For now, return mock data
        return {
            "plate_number": "BLA-123",
            "confidence": 98.2,
            "bbox": {"x": 0.32, "y": 0.55, "w": 0.36, "h": 0.14}
        }

    def match_vehicle(self, plate_number: str) -> Optional[Vehicle]:
        """Match detected plate with registered vehicles"""
        return self.vehicle_repo.get_by_plate_number(plate_number)

    def determine_status(self, vehicle: Optional[Vehicle]) -> DetectionStatus:
        """Determine detection status based on vehicle"""
        if not vehicle:
            return DetectionStatus.UNKNOWN
        
        status_map = {
            VehicleStatus.RESIDENT: DetectionStatus.RESIDENT,
            VehicleStatus.VISITOR: DetectionStatus.VISITOR,
            VehicleStatus.STAFF: DetectionStatus.STAFF,
            VehicleStatus.BLACKLIST: DetectionStatus.BLACKLIST
        }
        
        return status_map.get(vehicle.status, DetectionStatus.UNKNOWN)

    def create_detection(
        self,
        image_bytes: bytes,
        camera_id: Optional[UUID] = None,
        source: str = "live_upload"
    ) -> VehicleDetection:
        """Create vehicle detection record"""
        # Run detection
        detection_result = self.detect_plate(image_bytes, camera_id)
        
        # Match vehicle
        matched_vehicle = self.match_vehicle(detection_result["plate_number"])
        
        # Determine status
        status = self.determine_status(matched_vehicle)
        
        # Store images
        image_url = self.storage_util.upload_image(image_bytes, f"vehicle_detections/{datetime.utcnow().isoformat()}.jpg")
        full_frame_url = image_url  # Same for now, can be separate
        
        # Create detection record
        detection_data = {
            "plate_number": detection_result["plate_number"],
            "matched_vehicle_id": matched_vehicle.id if matched_vehicle else None,
            "status": status,
            "confidence": detection_result["confidence"],
            "camera_id": camera_id,
            "image_url": image_url,
            "full_frame_url": full_frame_url,
            "bbox": detection_result["bbox"],
            "source": source,
            "detected_at": datetime.utcnow()
        }
        
        return self.detection_repo.create(VehicleDetectionCreate(**detection_data))

    def take_action(
        self,
        detection_id: UUID,
        action: DetectionAction,
        acted_by: UUID,
        note: Optional[str] = None
    ) -> VehicleDetection:
        """Take action on detection"""
        detection = self.detection_repo.get(detection_id)
        if not detection:
            raise ValueError("Detection not found")
        
        detection.action_taken = action
        detection.acted_by = acted_by
        
        self.db.commit()
        self.db.refresh(detection)
        
        return detection
```

---

## 4.3 Face Recognition Service

**File**: `app/services/face_recognition_service.py`

```python
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import numpy as np
from app.models.person_model import Person, PersonRole
from app.models.face_detection_model import FaceDetection, FaceDetectionStatus, FaceDetectionAction
from app.models.face_embedding_model import FaceEmbedding
from app.repositories.person_repository import PersonRepository
from app.repositories.face_embedding_repository import FaceEmbeddingRepository
from app.repositories.face_detection_repository import FaceDetectionRepository
from app.utils.image_util import ImageUtil
from app.utils.storage_util import StorageUtil

class FaceRecognitionService:
    def __init__(self, db: Session):
        self.db = db
        self.person_repo = PersonRepository(db)
        self.embedding_repo = FaceEmbeddingRepository(db)
        self.detection_repo = FaceDetectionRepository(db)
        self.image_util = ImageUtil()
        self.storage_util = StorageUtil()

    def detect_face(self, image_bytes: bytes, camera_id: Optional[UUID] = None) -> Dict[str, Any]:
        """
        Detect face from image using YOLO-face
        Returns face bbox, confidence
        """
        # TODO: Integrate YOLO-face model
        return {
            "bbox": {"x": 0.4, "y": 0.2, "w": 0.2, "h": 0.35},
            "confidence": 96.4
        }

    def generate_embedding(self, image_bytes: bytes) -> List[float]:
        """
        Generate face embedding using ArcFace
        Returns 512-dimensional embedding vector
        """
        # TODO: Integrate ArcFace model
        # For now, return mock embedding
        return [0.1] * 512

    def match_face(self, embedding: List[float], threshold: float = 0.6) -> Optional[Person]:
        """Match face embedding with enrolled persons"""
        all_embeddings = self.embedding_repo.get_all_embeddings()
        
        best_match = None
        best_similarity = 0.0
        
        for emb_record in all_embeddings:
            stored_embedding = eval(emb_record.embedding)  # Parse JSON string
            similarity = self.cosine_similarity(embedding, stored_embedding)
            
            if similarity > best_similarity and similarity > threshold:
                best_similarity = similarity
                best_match = emb_record.person
        
        return best_match

    def cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two embeddings"""
        a_np = np.array(a)
        b_np = np.array(b)
        return np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np))

    def determine_status(self, person: Optional[Person]) -> FaceDetectionStatus:
        """Determine detection status based on person"""
        if not person:
            return FaceDetectionStatus.UNKNOWN
        
        from datetime import datetime
        now = datetime.utcnow()
        
        # Check if person is valid
        if not person.is_active:
            return FaceDetectionStatus.UNKNOWN
        
        if person.valid_until and person.valid_until < now:
            return FaceDetectionStatus.UNKNOWN
        
        status_map = {
            PersonRole.RESIDENT: FaceDetectionStatus.RESIDENT,
            PersonRole.STAFF: FaceDetectionStatus.STAFF,
            PersonRole.VISITOR: FaceDetectionStatus.VISITOR
        }
        
        return status_map.get(person.role, FaceDetectionStatus.UNKNOWN)

    def create_detection(
        self,
        image_bytes: bytes,
        camera_id: Optional[UUID] = None,
        source: str = "live_upload"
    ) -> FaceDetection:
        """Create face detection record"""
        # Detect face
        face_result = self.detect_face(image_bytes, camera_id)
        
        # Generate embedding
        embedding = self.generate_embedding(image_bytes)
        
        # Match face
        matched_person = self.match_face(embedding)
        
        # Determine status
        status = self.determine_status(matched_person)
        
        # Store images
        image_url = self.storage_util.upload_image(image_bytes, f"face_detections/{datetime.utcnow().isoformat()}.jpg")
        
        # Create detection record
        detection_data = {
            "matched_person_id": matched_person.id if matched_person else None,
            "status": status,
            "confidence": face_result["confidence"],
            "camera_id": camera_id,
            "image_url": image_url,
            "bbox": face_result["bbox"],
            "embedding": str(embedding),
            "source": source,
            "detected_at": datetime.utcnow()
        }
        
        return self.detection_repo.create(FaceDetectionCreate(**detection_data))

    def enroll_person(
        self,
        name: str,
        role: PersonRole,
        photos: List[bytes],
        flat_no: Optional[str] = None,
        phone: Optional[str] = None,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None
    ) -> Person:
        """Enroll new person with face embeddings"""
        # Create person
        person_data = {
            "name": name,
            "role": role,
            "flat_no": flat_no,
            "phone": phone,
            "valid_from": valid_from,
            "valid_until": valid_until,
            "created_at": datetime.utcnow()
        }
        
        person = self.person_repo.create(PersonCreate(**person_data))
        
        # Generate embeddings for each photo
        for i, photo in enumerate(photos):
            embedding = self.generate_embedding(photo)
            image_url = self.storage_util.upload_image(photo, f"persons/{person.id}/photo_{i}.jpg")
            
            embedding_data = {
                "person_id": person.id,
                "embedding": str(embedding),
                "image_url": image_url,
                "created_at": datetime.utcnow()
            }
            
            self.embedding_repo.create(FaceEmbeddingCreate(**embedding_data))
        
        # Update person photo_url with first photo
        person.photo_url = image_url
        self.db.commit()
        self.db.refresh(person)
        
        return person

    def take_action(
        self,
        detection_id: UUID,
        action: FaceDetectionAction,
        acted_by: UUID,
        note: Optional[str] = None
    ) -> FaceDetection:
        """Take action on detection"""
        detection = self.detection_repo.get(detection_id)
        if not detection:
            raise ValueError("Detection not found")
        
        detection.action_taken = action
        detection.acted_by = acted_by
        
        self.db.commit()
        self.db.refresh(detection)
        
        return detection
```

---

## 4.4 Alert Service

**File**: `app/services/alert_service.py`

```python
from typing import Optional, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.models.alert_model import Alert, AlertKind, AlertSeverity, AlertStatus
from app.models.vehicle_detection_model import VehicleDetection, DetectionStatus
from app.models.face_detection_model import FaceDetection, FaceDetectionStatus
from app.repositories.alert_repository import AlertRepository
from app.repositories.person_repository import PersonRepository
from app.schemas.alert_schema import AlertCreate

class AlertService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.person_repo = PersonRepository(db)

    def create_vehicle_alert(self, detection: VehicleDetection) -> Optional[Alert]:
        """Create alert based on vehicle detection"""
        if detection.status == DetectionStatus.BLACKLIST:
            return self._create_alert(
                kind=AlertKind.BLACKLIST,
                severity=AlertSeverity.HIGH,
                title="Blacklisted vehicle detected",
                description=f"Plate {detection.plate_number} attempted entry",
                camera_id=detection.camera_id,
                vehicle_detection_id=detection.id
            )
        elif detection.status == DetectionStatus.UNKNOWN:
            return self._create_alert(
                kind=AlertKind.UNKNOWN,
                severity=AlertSeverity.MEDIUM,
                title="Unknown vehicle detected",
                description=f"Plate {detection.plate_number} not registered",
                camera_id=detection.camera_id,
                vehicle_detection_id=detection.id
            )
        return None

    def create_face_alert(self, detection: FaceDetection) -> Optional[Alert]:
        """Create alert based on face detection"""
        if detection.matched_person:
            person = detection.matched_person
            
            # Check for expired visitor
            if person.valid_until and person.valid_until < datetime.utcnow():
                return self._create_alert(
                    kind=AlertKind.EXPIRED,
                    severity=AlertSeverity.MEDIUM,
                    title="Expired visitor pass",
                    description=f"Visitor {person.name} exceeded allowed window",
                    camera_id=detection.camera_id,
                    face_detection_id=detection.id
                )
        else:
            return self._create_alert(
                kind=AlertKind.UNKNOWN,
                severity=AlertSeverity.MEDIUM,
                title="Unknown face detected",
                description=f"No identity match. Confidence {detection.confidence}%",
                camera_id=detection.camera_id,
                face_detection_id=detection.id
            )
        return None

    def create_tailgate_alert(self, camera_id: UUID, description: str) -> Alert:
        """Create tailgating alert"""
        return self._create_alert(
            kind=AlertKind.TAILGATE,
            severity=AlertSeverity.HIGH,
            title="Possible tailgating",
            description=description,
            camera_id=camera_id
        )

    def _create_alert(
        self,
        kind: AlertKind,
        severity: AlertSeverity,
        title: str,
        description: str,
        camera_id: Optional[UUID] = None,
        vehicle_detection_id: Optional[UUID] = None,
        face_detection_id: Optional[UUID] = None
    ) -> Alert:
        """Internal method to create alert"""
        alert_data = {
            "kind": kind,
            "severity": severity,
            "title": title,
            "description": description,
            "camera_id": camera_id,
            "vehicle_detection_id": vehicle_detection_id,
            "face_detection_id": face_detection_id,
            "created_at": datetime.utcnow()
        }
        
        return self.alert_repo.create(AlertCreate(**alert_data))

    def resolve_alert(self, alert_id: UUID, resolved_by: UUID) -> Alert:
        """Resolve alert"""
        return self.alert_repo.resolve_alert(alert_id, resolved_by)

    def dismiss_alert(self, alert_id: UUID) -> Alert:
        """Dismiss alert"""
        return self.alert_repo.dismiss_alert(alert_id)

    def get_open_alerts(self, kind: Optional[AlertKind] = None, severity: Optional[AlertSeverity] = None) -> List[Alert]:
        """Get open alerts"""
        alerts, _ = self.alert_repo.get_open_alerts(kind=kind, severity=severity)
        return alerts
```

---

## 4.5 Camera Service

**File**: `app/services/camera_service.py`

```python
from typing import Optional
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.camera_model import Camera
from app.repositories.camera_repository import CameraRepository
from app.utils.stream_util import StreamUtil

class CameraService:
    def __init__(self, db: Session):
        self.db = db
        self.camera_repo = CameraRepository(db)
        self.stream_util = StreamUtil()

    def get_camera_stream(self, camera_id: UUID) -> Optional[str]:
        """Get MJPEG stream URL for camera"""
        camera = self.camera_repo.get(camera_id)
        if not camera or not camera.is_active:
            return None
        
        return self.stream_util.get_stream_url(camera.stream_url)

    def check_camera_health(self, camera_id: UUID) -> bool:
        """Check if camera is online"""
        camera = self.camera_repo.get(camera_id)
        if not camera:
            return False
        
        return self.stream_util.check_stream_health(camera.stream_url)
```

---

## 4.6 Storage Service

**File**: `app/services/storage_service.py`

```python
from typing import Optional
from app.utils.storage_util import StorageUtil

class StorageService:
    def __init__(self):
        self.storage_util = StorageUtil()

    def upload_image(self, image_bytes: bytes, key: str) -> str:
        """Upload image to storage"""
        return self.storage_util.upload_image(image_bytes, key)

    def get_image_url(self, key: str) -> str:
        """Get public URL for image"""
        return self.storage_util.get_image_url(key)

    def delete_image(self, key: str) -> bool:
        """Delete image from storage"""
        return self.storage_util.delete_image(key)
```

---

# 5. Controller Layer

## 5.1 User Controller

**File**: `app/controllers/user_controller.py`

```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

class UserController:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.auth_service = AuthService(db)

    def create_user(self, user_in: UserCreate) -> UserResponse:
        """Create new user"""
        user = self.auth_service.create_user(user_in)
        return UserResponse.model_validate(user)

    def get_user(self, user_id: UUID) -> Optional[UserResponse]:
        """Get user by ID"""
        user = self.user_repo.get(user_id)
        if not user:
            return None
        return UserResponse.model_validate(user)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users with pagination"""
        users, _ = self.user_repo.get_multi(skip, limit)
        return [UserResponse.model_validate(user) for user in users]

    def update_user(self, user_id: UUID, user_in: UserUpdate) -> Optional[UserResponse]:
        """Update user"""
        user = self.user_repo.get(user_id)
        if not user:
            return None
        updated_user = self.user_repo.update(user, user_in)
        return UserResponse.model_validate(updated_user)

    def delete_user(self, user_id: UUID) -> bool:
        """Delete user (soft delete)"""
        user = self.user_repo.soft_delete(user_id)
        return user is not None
```

---

## 5.2 Camera Controller

**File**: `app/controllers/camera_controller.py`

```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.camera_model import Camera
from app.schemas.camera_schema import CameraCreate, CameraUpdate, CameraResponse
from app.repositories.camera_repository import CameraRepository

class CameraController:
    def __init__(self, db: Session):
        self.db = db
        self.camera_repo = CameraRepository(db)

    def create_camera(self, camera_in: CameraCreate) -> CameraResponse:
        """Create new camera"""
        camera = self.camera_repo.create(camera_in)
        return CameraResponse.model_validate(camera)

    def get_camera(self, camera_id: UUID) -> Optional[CameraResponse]:
        """Get camera by ID"""
        camera = self.camera_repo.get(camera_id)
        if not camera:
            return None
        return CameraResponse.model_validate(camera)

    def get_cameras(self) -> List[CameraResponse]:
        """Get all cameras"""
        cameras = self.camera_repo.get_multi(0, 100)[0]
        return [CameraResponse.model_validate(camera) for camera in cameras]

    def update_camera(self, camera_id: UUID, camera_in: CameraUpdate) -> Optional[CameraResponse]:
        """Update camera"""
        camera = self.camera_repo.get(camera_id)
        if not camera:
            return None
        updated_camera = self.camera_repo.update(camera, camera_in)
        return CameraResponse.model_validate(updated_camera)

    def delete_camera(self, camera_id: UUID) -> bool:
        """Delete camera"""
        camera = self.camera_repo.delete(camera_id)
        return camera is not None
```

---

## 5.3 Vehicle Controller

**File**: `app/controllers/vehicle_controller.py`

```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.vehicle_model import Vehicle
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse
from app.repositories.vehicle_repository import VehicleRepository

class VehicleController:
    def __init__(self, db: Session):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)

    def create_vehicle(self, vehicle_in: VehicleCreate) -> VehicleResponse:
        """Create new vehicle"""
        # Check if plate number already exists
        if self.vehicle_repo.get_by_plate_number(vehicle_in.plate_number):
            raise ValueError("Vehicle with this plate number already exists")
        
        vehicle = self.vehicle_repo.create(vehicle_in)
        return VehicleResponse.model_validate(vehicle)

    def get_vehicle(self, vehicle_id: UUID) -> Optional[VehicleResponse]:
        """Get vehicle by ID"""
        vehicle = self.vehicle_repo.get(vehicle_id)
        if not vehicle:
            return None
        return VehicleResponse.model_validate(vehicle)

    def get_vehicles(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> VehicleListResponse:
        """Get vehicles with filters and pagination"""
        filters = {}
        if status:
            filters["status"] = status
        
        vehicles, total = self.vehicle_repo.get_multi(
            skip, limit, filters=filters, search=search, search_fields=["plate_number", "owner_name"]
        )
        
        return VehicleListResponse(
            items=[VehicleResponse.model_validate(v) for v in vehicles],
            total=total,
            limit=limit,
            offset=skip
        )

    def update_vehicle(self, vehicle_id: UUID, vehicle_in: VehicleUpdate) -> Optional[VehicleResponse]:
        """Update vehicle"""
        vehicle = self.vehicle_repo.get(vehicle_id)
        if not vehicle:
            return None
        updated_vehicle = self.vehicle_repo.update(vehicle, vehicle_in)
        return VehicleResponse.model_validate(updated_vehicle)

    def delete_vehicle(self, vehicle_id: UUID) -> bool:
        """Delete vehicle"""
        vehicle = self.vehicle_repo.delete(vehicle_id)
        return vehicle is not None
```

---

## 5.4 Vehicle Detection Controller

**File**: `app/controllers/vehicle_detection_controller.py`

```python
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.vehicle_detection_model import VehicleDetection
from app.schemas.vehicle_detection_schema import (
    VehicleDetectionResponse,
    VehicleDetectionActionRequest,
    VehicleDetectionActionResponse,
    VehicleDetectionListResponse
)
from app.repositories.vehicle_detection_repository import VehicleDetectionRepository
from app.services.alpr_service import ALPRService
from app.services.alert_service import AlertService

class VehicleDetectionController:
    def __init__(self, db: Session):
        self.db = db
        self.detection_repo = VehicleDetectionRepository(db)
        self.alpr_service = ALPRService(db)
        self.alert_service = AlertService(db)

    def detect_vehicle(
        self,
        image_bytes: bytes,
        camera_id: Optional[UUID] = None
    ) -> VehicleDetectionResponse:
        """Detect vehicle from image"""
        detection = self.alpr_service.create_detection(image_bytes, camera_id)
        
        # Create alert if needed
        alert = self.alert_service.create_vehicle_alert(detection)
        
        return VehicleDetectionResponse.model_validate(detection)

    def get_detections(
        self,
        camera_id: Optional[UUID] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> VehicleDetectionListResponse:
        """Get vehicle detections with filters"""
        from datetime import datetime
        
        from_dt = datetime.fromisoformat(from_date) if from_date else None
        to_dt = datetime.fromisoformat(to_date) if to_date else None
        
        detections, total = self.detection_repo.get_recent_detections(
            camera_id=camera_id,
            status=status,
            from_date=from_dt,
            to_date=to_dt,
            search=search,
            skip=skip,
            limit=limit
        )
        
        stats = self.detection_repo.get_statistics(from_dt)
        
        return VehicleDetectionListResponse(
            items=[VehicleDetectionResponse.model_validate(d) for d in detections],
            total=total,
            limit=limit,
            offset=skip,
            stats=stats
        )

    def take_action(
        self,
        detection_id: UUID,
        action_request: VehicleDetectionActionRequest,
        acted_by: UUID
    ) -> VehicleDetectionActionResponse:
        """Take action on detection"""
        detection = self.alpr_service.take_action(
            detection_id,
            action_request.action,
            acted_by,
            action_request.note
        )
        
        return VehicleDetectionActionResponse(
            ok=True,
            action_taken=detection.action_taken,
            acted_by=acted_by
        )
```

---

## 5.5 Person Controller

**File**: `app/controllers/person_controller.py`

```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.person_model import Person
from app.schemas.person_schema import PersonCreate, PersonUpdate, PersonResponse, PersonListResponse
from app.repositories.person_repository import PersonRepository
from app.services.face_recognition_service import FaceRecognitionService

class PersonController:
    def __init__(self, db: Session):
        self.db = db
        self.person_repo = PersonRepository(db)
        self.face_service = FaceRecognitionService(db)

    def enroll_person(
        self,
        name: str,
        role: str,
        photos: List[bytes],
        flat_no: Optional[str] = None,
        phone: Optional[str] = None,
        valid_from: Optional[str] = None,
        valid_until: Optional[str] = None
    ) -> PersonResponse:
        """Enroll new person with face embeddings"""
        from datetime import datetime
        from app.models.person_model import PersonRole
        
        from_dt = datetime.fromisoformat(valid_from) if valid_from else None
        to_dt = datetime.fromisoformat(valid_until) if valid_until else None
        
        person = self.face_service.enroll_person(
            name=name,
            role=PersonRole(role),
            photos=photos,
            flat_no=flat_no,
            phone=phone,
            valid_from=from_dt,
            valid_until=to_dt
        )
        
        return PersonResponse.model_validate(person)

    def get_person(self, person_id: UUID) -> Optional[PersonResponse]:
        """Get person by ID"""
        person = self.person_repo.get(person_id)
        if not person:
            return None
        
        # Get embeddings count
        from app.repositories.face_embedding_repository import FaceEmbeddingRepository
        embedding_repo = FaceEmbeddingRepository(self.db)
        embeddings = embedding_repo.get_by_person_id(person_id)
        
        response = PersonResponse.model_validate(person)
        response.embeddings_count = len(embeddings)
        return response

    def get_persons(
        self,
        search: Optional[str] = None,
        role: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> PersonListResponse:
        """Get persons with filters and pagination"""
        from app.models.person_model import PersonRole
        
        filters = {}
        if role:
            filters["role"] = PersonRole(role)
        
        persons, total = self.person_repo.get_multi(
            skip, limit, filters=filters, search=search, search_fields=["name", "flat_no"]
        )
        
        return PersonListResponse(
            items=[PersonResponse.model_validate(p) for p in persons],
            total=total,
            limit=limit,
            offset=skip
        )

    def update_person(self, person_id: UUID, person_in: PersonUpdate) -> Optional[PersonResponse]:
        """Update person"""
        person = self.person_repo.get(person_id)
        if not person:
            return None
        updated_person = self.person_repo.update(person, person_in)
        return PersonResponse.model_validate(updated_person)

    def delete_person(self, person_id: UUID) -> bool:
        """Delete person"""
        person = self.person_repo.delete(person_id)
        return person is not None

    def add_photos(self, person_id: UUID, photos: List[bytes]) -> PersonResponse:
        """Add more reference photos to person"""
        from app.repositories.face_embedding_repository import FaceEmbeddingRepository
        from app.schemas.face_embedding_schema import FaceEmbeddingCreate
        from datetime import datetime
        from app.utils.storage_util import StorageUtil
        
        person = self.person_repo.get(person_id)
        if not person:
            raise ValueError("Person not found")
        
        embedding_repo = FaceEmbeddingRepository(self.db)
        storage_util = StorageUtil()
        
        for i, photo in enumerate(photos):
            embedding = self.face_service.generate_embedding(photo)
            image_url = storage_util.upload_image(photo, f"persons/{person_id}/photo_{datetime.utcnow().timestamp()}.jpg")
            
            embedding_data = {
                "person_id": person_id,
                "embedding": str(embedding),
                "image_url": image_url,
                "created_at": datetime.utcnow()
            }
            
            embedding_repo.create(FaceEmbeddingCreate(**embedding_data))
        
        return self.get_person(person_id)
```

---

## 5.6 Face Detection Controller

**File**: `app/controllers/face_detection_controller.py`

```python
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.face_detection_model import FaceDetection
from app.schemas.face_detection_schema import (
    FaceDetectionResponse,
    FaceDetectionActionRequest,
    FaceDetectionActionResponse,
    FaceDetectionListResponse
)
from app.repositories.face_detection_repository import FaceDetectionRepository
from app.services.face_recognition_service import FaceRecognitionService
from app.services.alert_service import AlertService

class FaceDetectionController:
    def __init__(self, db: Session):
        self.db = db
        self.detection_repo = FaceDetectionRepository(db)
        self.face_service = FaceRecognitionService(db)
        self.alert_service = AlertService(db)

    def detect_face(
        self,
        image_bytes: bytes,
        camera_id: Optional[UUID] = None
    ) -> FaceDetectionResponse:
        """Detect face from image"""
        detection = self.face_service.create_detection(image_bytes, camera_id)
        
        # Create alert if needed
        alert = self.alert_service.create_face_alert(detection)
        
        return FaceDetectionResponse.model_validate(detection)

    def get_detections(
        self,
        camera_id: Optional[UUID] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> FaceDetectionListResponse:
        """Get face detections with filters"""
        from datetime import datetime
        
        from_dt = datetime.fromisoformat(from_date) if from_date else None
        to_dt = datetime.fromisoformat(to_date) if to_date else None
        
        detections, total = self.detection_repo.get_recent_detections(
            camera_id=camera_id,
            status=status,
            from_date=from_dt,
            to_date=to_dt,
            skip=skip,
            limit=limit
        )
        
        stats = self.detection_repo.get_statistics(from_dt)
        
        return FaceDetectionListResponse(
            items=[FaceDetectionResponse.model_validate(d) for d in detections],
            total=total,
            limit=limit,
            offset=skip,
            stats=stats
        )

    def take_action(
        self,
        detection_id: UUID,
        action_request: FaceDetectionActionRequest,
        acted_by: UUID
    ) -> FaceDetectionActionResponse:
        """Take action on detection"""
        detection = self.face_service.take_action(
            detection_id,
            action_request.action,
            acted_by,
            action_request.note
        )
        
        return FaceDetectionActionResponse(
            ok=True,
            action_taken=detection.action_taken,
            acted_by=acted_by
        )
```

---

## 5.7 Alert Controller

**File**: `app/controllers/alert_controller.py`

```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.alert_model import Alert
from app.schemas.alert_schema import (
    AlertResponse,
    AlertResolveRequest,
    AlertResolveResponse,
    AlertListResponse
)
from app.repositories.alert_repository import AlertRepository
from app.services.alert_service import AlertService

class AlertController:
    def __init__(self, db: Session):
        self.db = db
        self.alert_repo = AlertRepository(db)
        self.alert_service = AlertService(db)

    def get_alerts(
        self,
        status: Optional[str] = None,
        severity: Optional[str] = None,
        kind: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> AlertListResponse:
        """Get alerts with filters"""
        from app.models.alert_model import AlertStatus, AlertSeverity, AlertKind
        
        kind_enum = AlertKind(kind) if kind else None
        severity_enum = AlertSeverity(severity) if severity else None
        
        alerts, total = self.alert_repo.get_open_alerts(
            kind=kind_enum,
            severity=severity_enum,
            skip=skip,
            limit=limit
        )
        
        unread = self.alert_repo.get_unread_count()
        
        return AlertListResponse(
            items=[AlertResponse.model_validate(a) for a in alerts],
            total=total,
            unread=unread,
            limit=limit,
            offset=skip
        )

    def resolve_alert(
        self,
        alert_id: UUID,
        resolve_request: AlertResolveRequest,
        resolved_by: UUID
    ) -> AlertResolveResponse:
        """Resolve alert"""
        self.alert_service.resolve_alert(alert_id, resolved_by)
        return AlertResolveResponse(ok=True)

    def dismiss_alert(self, alert_id: UUID) -> AlertResolveResponse:
        """Dismiss alert"""
        self.alert_service.dismiss_alert(alert_id)
        return AlertResolveResponse(ok=True)
```

---

## 5.8 Entry Log Controller

**File**: `app/controllers/entry_log_controller.py`

```python
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.entry_log_model import EntryLog
from app.schemas.entry_log_schema import EntryLogResponse, EntryLogListResponse
from app.repositories.entry_log_repository import EntryLogRepository

class EntryLogController:
    def __init__(self, db: Session):
        self.db = db
        self.log_repo = EntryLogRepository(db)

    def get_logs(
        self,
        detection_type: Optional[str] = None,
        camera_id: Optional[UUID] = None,
        status: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> EntryLogListResponse:
        """Get entry logs with filters"""
        from datetime import datetime
        from app.models.entry_log_model import EntryLogType, EntryLogStatus
        
        type_enum = EntryLogType(detection_type) if detection_type else None
        status_enum = EntryLogStatus(status) if status else None
        
        from_dt = datetime.fromisoformat(from_date) if from_date else None
        to_dt = datetime.fromisoformat(to_date) if to_date else None
        
        logs, total = self.log_repo.get_logs(
            detection_type=type_enum,
            camera_id=camera_id,
            status=status_enum,
            from_date=from_dt,
            to_date=to_dt,
            skip=skip,
            limit=limit
        )
        
        return EntryLogListResponse(
            items=[EntryLogResponse.model_validate(log) for log in logs],
            total=total,
            limit=limit,
            offset=skip
        )
```

---

# 6. API Routes

## 6.1 User Routes

**File**: `app/edge/http/routes/user_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.di.container import get_db
from app.controllers.user_controller import UserController
from app.schemas.user_schema import UserCreate, UserUpdate, UserResponse
from app.middlewares.auth_middleware import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

def get_user_controller(db: Session = Depends(get_db)) -> UserController:
    return UserController(db)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    controller: UserController = Depends(get_user_controller)
):
    """Create new user"""
    return controller.create_user(user_in)

@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: dict = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    """Get all users (authenticated)"""
    return controller.get_users(skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    """Get user by ID"""
    user = controller.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_in: UserUpdate,
    current_user: dict = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    """Update user"""
    user = controller.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: UserController = Depends(get_user_controller)
):
    """Delete user"""
    if not controller.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
```

---

## 6.2 Camera Routes

**File**: `app/edge/http/routes/camera_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.di.container import get_db
from app.controllers.camera_controller import CameraController
from app.schemas.camera_schema import CameraCreate, CameraUpdate, CameraResponse
from app.middlewares.auth_middleware import get_current_user

router = APIRouter(prefix="/api/cameras", tags=["cameras"])

def get_camera_controller(db: Session = Depends(get_db)) -> CameraController:
    return CameraController(db)

@router.post("/", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
def create_camera(
    camera_in: CameraCreate,
    current_user: dict = Depends(get_current_user),
    controller: CameraController = Depends(get_camera_controller)
):
    """Create new camera"""
    return controller.create_camera(camera_in)

@router.get("/", response_model=List[CameraResponse])
def get_cameras(
    current_user: dict = Depends(get_current_user),
    controller: CameraController = Depends(get_camera_controller)
):
    """Get all cameras"""
    return controller.get_cameras()

@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(
    camera_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: CameraController = Depends(get_camera_controller)
):
    """Get camera by ID"""
    camera = controller.get_camera(camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.patch("/{camera_id}", response_model=CameraResponse)
def update_camera(
    camera_id: UUID,
    camera_in: CameraUpdate,
    current_user: dict = Depends(get_current_user),
    controller: CameraController = Depends(get_camera_controller)
):
    """Update camera"""
    camera = controller.update_camera(camera_id, camera_in)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.delete("/{camera_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_camera(
    camera_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: CameraController = Depends(get_camera_controller)
):
    """Delete camera"""
    if not controller.delete_camera(camera_id):
        raise HTTPException(status_code=404, detail="Camera not found")

@router.get("/{camera_id}/stream")
def get_camera_stream(
    camera_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: CameraController = Depends(get_camera_controller)
):
    """Get camera stream (MJPEG)"""
    from fastapi.responses import StreamingResponse
    from app.services.camera_service import CameraService
    
    camera_service = CameraService(controller.db)
    stream_url = camera_service.get_camera_stream(camera_id)
    
    if not stream_url:
        raise HTTPException(status_code=404, detail="Camera not found or inactive")
    
    # Return streaming response
    # Implementation depends on stream_util
    return StreamingResponse(stream_url, media_type="multipart/x-mixed-replace; boundary=frame")
```

---

## 6.3 Vehicle Routes

**File**: `app/edge/http/routes/vehicle_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.di.container import get_db
from app.controllers.vehicle_controller import VehicleController
from app.schemas.vehicle_schema import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse
from app.middlewares.auth_middleware import get_current_user

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])

def get_vehicle_controller(db: Session = Depends(get_db)) -> VehicleController:
    return VehicleController(db)

@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_in: VehicleCreate,
    current_user: dict = Depends(get_current_user),
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Register new vehicle"""
    return controller.create_vehicle(vehicle_in)

@router.get("/", response_model=VehicleListResponse)
def get_vehicles(
    search: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_user),
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Get vehicles with filters"""
    return controller.get_vehicles(search, status, skip, limit)

@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Get vehicle by ID"""
    vehicle = controller.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.patch("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: UUID,
    vehicle_in: VehicleUpdate,
    current_user: dict = Depends(get_current_user),
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Update vehicle"""
    vehicle = controller.update_vehicle(vehicle_id, vehicle_in)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle

@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: VehicleController = Depends(get_vehicle_controller)
):
    """Delete vehicle"""
    if not controller.delete_vehicle(vehicle_id):
        raise HTTPException(status_code=404, detail="Vehicle not found")
```

---

## 6.4 Vehicle Detection Routes

**File**: `app/edge/http/routes/vehicle_detection_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.di.container import get_db
from app.controllers.vehicle_detection_controller import VehicleDetectionController
from app.schemas.vehicle_detection_schema import (
    VehicleDetectionResponse,
    VehicleDetectionActionRequest,
    VehicleDetectionActionResponse,
    VehicleDetectionListResponse
)
from app.middlewares.auth_middleware import get_current_user

router = APIRouter(prefix="/api/vehicles", tags=["vehicle-detections"])

def get_vehicle_detection_controller(db: Session = Depends(get_db)) -> VehicleDetectionController:
    return VehicleDetectionController(db)

@router.post("/detect", response_model=VehicleDetectionResponse)
def detect_vehicle(
    file: UploadFile = File(...),
    camera_id: Optional[UUID] = Form(None),
    current_user: dict = Depends(get_current_user),
    controller: VehicleDetectionController = Depends(get_vehicle_detection_controller)
):
    """Run YOLO + OCR on uploaded image"""
    image_bytes = file.file.read()
    return controller.detect_vehicle(image_bytes, camera_id)

@router.get("/detections", response_model=VehicleDetectionListResponse)
def get_vehicle_detections(
    camera_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_user),
    controller: VehicleDetectionController = Depends(get_vehicle_detection_controller)
):
    """Get vehicle detections with filters"""
    return controller.get_detections(camera_id, status, from_date, to_date, search, skip, limit)

@router.post("/detections/{detection_id}/action", response_model=VehicleDetectionActionResponse)
def take_vehicle_action(
    detection_id: UUID,
    action_request: VehicleDetectionActionRequest,
    current_user: dict = Depends(get_current_user),
    controller: VehicleDetectionController = Depends(get_vehicle_detection_controller)
):
    """Take action on vehicle detection"""
    return controller.take_action(detection_id, action_request, UUID(current_user["sub"]))
```

---

## 6.5 Person Routes

**File**: `app/edge/http/routes/person_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional, List
from uuid import UUID

from app.di.container import get_db
from app.controllers.person_controller import PersonController
from app.schemas.person_schema import PersonCreate, PersonUpdate, PersonResponse, PersonListResponse
from app.middlewares.auth_middleware import get_current_user

router = APIRouter(prefix="/api/faces/persons", tags=["persons"])

def get_person_controller(db: Session = Depends(get_db)) -> PersonController:
    return PersonController(db)

@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def enroll_person(
    name: str = Form(...),
    role: str = Form(...),
    flat_no: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    valid_from: Optional[str] = Form(None),
    valid_until: Optional[str] = Form(None),
    photos: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
    controller: PersonController = Depends(get_person_controller)
):
    """Enroll new person with face photos"""
    photo_bytes = [photo.file.read() for photo in photos]
    return controller.enroll_person(name, role, photo_bytes, flat_no, phone, valid_from, valid_until)

@router.get("/", response_model=PersonListResponse)
def get_persons(
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_user),
    controller: PersonController = Depends(get_person_controller)
):
    """Get enrolled persons"""
    return controller.get_persons(search, role, skip, limit)

@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: PersonController = Depends(get_person_controller)
):
    """Get person by ID"""
    person = controller.get_person(person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@router.patch("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: UUID,
    person_in: PersonUpdate,
    current_user: dict = Depends(get_current_user),
    controller: PersonController = Depends(get_person_controller)
):
    """Update person"""
    person = controller.update_person(person_id, person_in)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person

@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(
    person_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: PersonController = Depends(get_person_controller)
):
    """Delete person"""
    if not controller.delete_person(person_id):
        raise HTTPException(status_code=404, detail="Person not found")

@router.post("/{person_id}/photos", response_model=PersonResponse)
def add_person_photos(
    person_id: UUID,
    photos: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user),
    controller: PersonController = Depends(get_person_controller)
):
    """Add more reference photos to person"""
    photo_bytes = [photo.file.read() for photo in photos]
    return controller.add_photos(person_id, photo_bytes)
```

---

## 6.6 Face Detection Routes

**File**: `app/edge/http/routes/face_detection_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.di.container import get_db
from app.controllers.face_detection_controller import FaceDetectionController
from app.schemas.face_detection_schema import (
    FaceDetectionResponse,
    FaceDetectionActionRequest,
    FaceDetectionActionResponse,
    FaceDetectionListResponse
)
from app.middlewares.auth_middleware import get_current_user

router = APIRouter(prefix="/api/faces", tags=["face-detections"])

def get_face_detection_controller(db: Session = Depends(get_db)) -> FaceDetectionController:
    return FaceDetectionController(db)

@router.post("/detect", response_model=FaceDetectionResponse)
def detect_face(
    file: UploadFile = File(...),
    camera_id: Optional[UUID] = Form(None),
    current_user: dict = Depends(get_current_user),
    controller: FaceDetectionController = Depends(get_face_detection_controller)
):
    """Run YOLO-face + embedding match on image"""
    image_bytes = file.file.read()
    return controller.detect_face(image_bytes, camera_id)

@router.get("/detections", response_model=FaceDetectionListResponse)
def get_face_detections(
    camera_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_user),
    controller: FaceDetectionController = Depends(get_face_detection_controller)
):
    """Get face detections with filters"""
    return controller.get_detections(camera_id, status, from_date, to_date, skip, limit)

@router.post("/detections/{detection_id}/action", response_model=FaceDetectionActionResponse)
def take_face_action(
    detection_id: UUID,
    action_request: FaceDetectionActionRequest,
    current_user: dict = Depends(get_current_user),
    controller: FaceDetectionController = Depends(get_face_detection_controller)
):
    """Take action on face detection"""
    return controller.take_action(detection_id, action_request, UUID(current_user["sub"]))
```

---

## 6.7 Alert Routes

**File**: `app/edge/http/routes/alert_route.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.di.container import get_db
from app.controllers.alert_controller import AlertController
from app.schemas.alert_schema import (
    AlertResponse,
    AlertResolveRequest,
    AlertResolveResponse,
    AlertListResponse
)
from app.middlewares.auth_middleware import get_current_user

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

def get_alert_controller(db: Session = Depends(get_db)) -> AlertController:
    return AlertController(db)

@router.get("/", response_model=AlertListResponse)
def get_alerts(
    status: Optional[str] = Query("open"),
    severity: Optional[str] = Query(None),
    kind: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_user),
    controller: AlertController = Depends(get_alert_controller)
):
    """Get alerts with filters"""
    return controller.get_alerts(status, severity, kind, skip, limit)

@router.post("/{alert_id}/resolve", response_model=AlertResolveResponse)
def resolve_alert(
    alert_id: UUID,
    resolve_request: AlertResolveRequest,
    current_user: dict = Depends(get_current_user),
    controller: AlertController = Depends(get_alert_controller)
):
    """Resolve alert"""
    return controller.resolve_alert(alert_id, resolve_request, UUID(current_user["sub"]))

@router.post("/{alert_id}/dismiss", response_model=AlertResolveResponse)
def dismiss_alert(
    alert_id: UUID,
    current_user: dict = Depends(get_current_user),
    controller: AlertController = Depends(get_alert_controller)
):
    """Dismiss alert"""
    return controller.dismiss_alert(alert_id)
```

---

## 6.8 Entry Log Routes

**File**: `app/edge/http/routes/entry_log_route.py`

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.di.container import get_db
from app.controllers.entry_log_controller import EntryLogController
from app.schemas.entry_log_schema import EntryLogListResponse
from app.middlewares.auth_middleware import get_current_user

router = APIRouter(prefix="/api/logs", tags=["logs"])

def get_entry_log_controller(db: Session = Depends(get_db)) -> EntryLogController:
    return EntryLogController(db)

@router.get("/", response_model=EntryLogListResponse)
def get_logs(
    type: Optional[str] = Query("all"),
    camera_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None),
    to_date: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    current_user: dict = Depends(get_current_user),
    controller: EntryLogController = Depends(get_entry_log_controller)
):
    """Get entry logs with filters"""
    return controller.get_logs(type, camera_id, status, from_date, to_date, skip, limit)
```

---

## 6.9 Auth Routes

**File**: `app/edge/http/routes/auth_route.py` (extend existing)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.di.container import get_db
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserLogin, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])

def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)

@router.post("/login", response_model=TokenResponse)
def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user and return tokens"""
    try:
        return auth_service.login(credentials)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
```

---

## 6.10 Health Route

**File**: `app/edge/http/routes/health_route.py` (extend existing)

```python
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "smart-surveillance-backend"}
```

---

# 7. WebSocket Implementation

## 7.1 Surveillance WebSocket Handler

**File**: `app/edge/socket/surveillance_socket_handler.py`

```python
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from uuid import UUID
import json
import asyncio

class SurveillanceSocketHandler:
    def __init__(self):
        self.active_connections: Dict[UUID, Set[WebSocket]] = {}
        self.camera_subscriptions: Dict[WebSocket, Set[UUID]] = {}

    async def connect(self, websocket: WebSocket, camera_id: UUID):
        """Connect WebSocket for camera"""
        await websocket.accept()
        
        if camera_id not in self.active_connections:
            self.active_connections[camera_id] = set()
        
        self.active_connections[camera_id].add(websocket)
        
        if websocket not in self.camera_subscriptions:
            self.camera_subscriptions[websocket] = set()
        
        self.camera_subscriptions[websocket].add(camera_id)

    def disconnect(self, websocket: WebSocket):
        """Disconnect WebSocket"""
        if websocket in self.camera_subscriptions:
            for camera_id in self.camera_subscriptions[websocket]:
                if camera_id in self.active_connections:
                    self.active_connections[camera_id].discard(websocket)
            
            del self.camera_subscriptions[websocket]

    async def broadcast_vehicle_detection(self, camera_id: UUID, detection_data: dict):
        """Broadcast vehicle detection to subscribed clients"""
        if camera_id in self.active_connections:
            message = {
                "type": "vehicle_detection",
                "data": detection_data
            }
            
            for connection in self.active_connections[camera_id].copy():
                try:
                    await connection.send_json(message)
                except:
                    self.disconnect(connection)

    async def broadcast_face_detection(self, camera_id: UUID, detection_data: dict):
        """Broadcast face detection to subscribed clients"""
        if camera_id in self.active_connections:
            message = {
                "type": "face_detection",
                "data": detection_data
            }
            
            for connection in self.active_connections[camera_id].copy():
                try:
                    await connection.send_json(message)
                except:
                    self.disconnect(connection)

    async def broadcast_alert(self, camera_id: UUID, alert_data: dict):
        """Broadcast alert to subscribed clients"""
        if camera_id in self.active_connections:
            message = {
                "type": "alert",
                "data": alert_data
            }
            
            for connection in self.active_connections[camera_id].copy():
                try:
                    await connection.send_json(message)
                except:
                    self.disconnect(connection)

    async def broadcast_camera_status(self, camera_id: UUID, online: bool):
        """Broadcast camera status to subscribed clients"""
        if camera_id in self.active_connections:
            message = {
                "type": "camera_status",
                "data": {
                    "camera_id": str(camera_id),
                    "online": online
                }
            }
            
            for connection in self.active_connections[camera_id].copy():
                try:
                    await connection.send_json(message)
                except:
                    self.disconnect(connection)

# Global instance
surveillance_handler = SurveillanceSocketHandler()
```

---

## 7.2 Surveillance WebSocket Route

**File**: `app/edge/socket/surveillance_socket_route.py`

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends
from uuid import UUID
from app.edge.socket.surveillance_socket_handler import surveillance_handler
from app.middlewares.auth_middleware import verify_websocket_token

router = APIRouter()

@router.websocket("/ws/surveillance")
async def surveillance_websocket(
    websocket: WebSocket,
    camera_id: UUID = Query(...),
    token: str = Query(...)
):
    """WebSocket endpoint for real-time surveillance updates"""
    # Verify token
    user = verify_websocket_token(token)
    if not user:
        await websocket.close(code=1008)
        return
    
    # Connect
    await surveillance_handler.connect(websocket, camera_id)
    
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Handle client messages if needed
    except WebSocketDisconnect:
        surveillance_handler.disconnect(websocket)
```

---

# 8. AI Integration

## 8.1 AI Configuration

**File**: `app/configs/ai_config.py`

```python
from pydantic import BaseSettings

class AIConfig(BaseSettings):
    # YOLO Configuration
    YOLO_VEHICLE_MODEL_PATH: str = "models/yolo/vehicle.pt"
    YOLO_FACE_MODEL_PATH: str = "models/yolo/face.pt"
    YOLO_CONFIDENCE_THRESHOLD: float = 0.5
    
    # OCR Configuration
    OCR_MODEL_PATH: str = "models/ocr"
    OCR_CONFIDENCE_THRESHOLD: float = 0.8
    
    # Face Recognition Configuration
    ARCFACE_MODEL_PATH: str = "models/arcface"
    FACE_EMBEDDING_DIM: int = 512
    FACE_SIMILARITY_THRESHOLD: float = 0.6
    
    # Detection Configuration
    MAX_DETECTIONS_PER_IMAGE: int = 10
    PLATE_CONFIDENCE_THRESHOLD: float = 0.7
    FACE_CONFIDENCE_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"

ai_config = AIConfig()
```

---

## 8.2 ALPR Service (Real Implementation)

**File**: `app/services/alpr_service.py` (update with real AI)

```python
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import cv2
import numpy as np
from ultralytics import YOLO
from paddleocr import PaddleOCR
from app.models.vehicle_detection_model import VehicleDetection, DetectionStatus, DetectionAction
from app.models.vehicle_model import Vehicle, VehicleStatus
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.vehicle_detection_repository import VehicleDetectionRepository
from app.utils.image_util import ImageUtil
from app.utils.storage_util import StorageUtil
from app.configs.ai_config import ai_config

class ALPRService:
    def __init__(self, db: Session):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)
        self.detection_repo = VehicleDetectionRepository(db)
        self.image_util = ImageUtil()
        self.storage_util = StorageUtil()
        
        # Load models
        self.yolo_model = YOLO(ai_config.YOLO_VEHICLE_MODEL_PATH)
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def detect_plate(self, image_bytes: bytes, camera_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Detect license plate from image using YOLO + OCR"""
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Run YOLO detection
        results = self.yolo_model(image)
        
        # Process detections
        for result in results:
            boxes = result.boxes
            for box in boxes:
                if box.conf > ai_config.YOLO_CONFIDENCE_THRESHOLD:
                    # Get bbox
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox = {
                        "x": float(x1 / image.shape[1]),
                        "y": float(y1 / image.shape[0]),
                        "w": float((x2 - x1) / image.shape[1]),
                        "h": float((y2 - y1) / image.shape[0])
                    }
                    
                    # Crop plate region
                    plate_crop = image[int(y1):int(y2), int(x1):int(x2)]
                    
                    # Run OCR
                    ocr_result = self.ocr.ocr(plate_crop, cls=True)
                    
                    if ocr_result and ocr_result[0]:
                        plate_text = ocr_result[0][0][1][0]
                        confidence = ocr_result[0][0][1][1]
                        
                        return {
                            "plate_number": plate_text,
                            "confidence": float(confidence * 100),
                            "bbox": bbox
                        }
        
        # No detection
        return {
            "plate_number": None,
            "confidence": 0.0,
            "bbox": None
        }

    # ... rest of the methods remain the same
```

---

## 8.3 Face Recognition Service (Real Implementation)

**File**: `app/services/face_recognition_service.py` (update with real AI)

```python
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
import cv2
import numpy as np
from ultralytics import YOLO
from insightface.app import FaceAnalysis
from app.models.person_model import Person, PersonRole
from app.models.face_detection_model import FaceDetection, FaceDetectionStatus, FaceDetectionAction
from app.models.face_embedding_model import FaceEmbedding
from app.repositories.person_repository import PersonRepository
from app.repositories.face_embedding_repository import FaceEmbeddingRepository
from app.repositories.face_detection_repository import FaceDetectionRepository
from app.utils.image_util import ImageUtil
from app.utils.storage_util import StorageUtil
from app.configs.ai_config import ai_config

class FaceRecognitionService:
    def __init__(self, db: Session):
        self.db = db
        self.person_repo = PersonRepository(db)
        self.embedding_repo = FaceEmbeddingRepository(db)
        self.detection_repo = FaceDetectionRepository(db)
        self.image_util = ImageUtil()
        self.storage_util = StorageUtil()
        
        # Load models
        self.yolo_face = YOLO(ai_config.YOLO_FACE_MODEL_PATH)
        self.face_analysis = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
        self.face_analysis.prepare(ctx_id=0, det_size=(640, 640))

    def detect_face(self, image_bytes: bytes, camera_id: Optional[UUID] = None) -> Dict[str, Any]:
        """Detect face from image using YOLO-face"""
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Run YOLO-face detection
        results = self.yolo_face(image)
        
        # Get first face
        for result in results:
            boxes = result.boxes
            if len(boxes) > 0:
                box = boxes[0]
                if box.conf > ai_config.YOLO_CONFIDENCE_THRESHOLD:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox = {
                        "x": float(x1 / image.shape[1]),
                        "y": float(y1 / image.shape[0]),
                        "w": float((x2 - x1) / image.shape[1]),
                        "h": float((y2 - y1) / image.shape[0])
                    }
                    
                    return {
                        "bbox": bbox,
                        "confidence": float(box.conf * 100)
                    }
        
        return {
            "bbox": None,
            "confidence": 0.0
        }

    def generate_embedding(self, image_bytes: bytes) -> List[float]:
        """Generate face embedding using ArcFace"""
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Run face analysis
        faces = self.face_analysis.get(image)
        
        if len(faces) > 0:
            embedding = faces[0].embedding
            return embedding.tolist()
        
        return [0.0] * ai_config.FACE_EMBEDDING_DIM

    # ... rest of the methods remain the same
```

---

# 9. Configuration

## 9.1 Storage Configuration

**File**: `app/configs/storage_config.py`

```python
from pydantic import BaseSettings

class StorageConfig(BaseSettings):
    # S3/MinIO Configuration
    STORAGE_TYPE: str = "s3"  # s3 or local
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "smart-surveillance"
    S3_REGION: str = "us-east-1"
    
    # Local Storage Configuration
    LOCAL_STORAGE_PATH: str = "./storage"
    
    # Image Configuration
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/jpg"]
    
    class Config:
        env_file = ".env"

storage_config = StorageConfig()
```

---

## 9.2 Camera Configuration

**File**: `app/configs/camera_config.py`

```python
from pydantic import BaseSettings

class CameraConfig(BaseSettings):
    # Stream Configuration
    STREAM_BUFFER_SIZE: int = 1024 * 1024  # 1MB
    STREAM_TIMEOUT: int = 30  # seconds
    STREAM_RETRY_ATTEMPTS: int = 3
    STREAM_HEALTH_CHECK_INTERVAL: int = 60  # seconds
    
    # MJPEG Configuration
    MJPEG_QUALITY: int = 85
    MJPEG_FPS: int = 15
    
    class Config:
        env_file = ".env"

camera_config = CameraConfig()
```

---

# 10. Utilities

## 10.1 Image Utility

**File**: `app/utils/image_util.py`

```python
import cv2
import numpy as np
from typing import Tuple, Optional

class ImageUtil:
    def __init__(self):
        pass

    def validate_image(self, image_bytes: bytes) -> bool:
        """Validate image format and size"""
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return image is not None
        except:
            return False

    def resize_image(self, image_bytes: bytes, max_size: Tuple[int, int] = (1920, 1080)) -> bytes:
        """Resize image to max dimensions"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        h, w = image.shape[:2]
        max_w, max_h = max_size
        
        if w > max_w or h > max_h:
            scale = min(max_w / w, max_h / h)
            new_w = int(w * scale)
            new_h = int(h * scale)
            image = cv2.resize(image, (new_w, new_h))
        
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()

    def crop_bbox(self, image_bytes: bytes, bbox: dict) -> bytes:
        """Crop image based on bbox"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        h, w = image.shape[:2]
        x = int(bbox["x"] * w)
        y = int(bbox["y"] * h)
        bw = int(bbox["w"] * w)
        bh = int(bbox["h"] * h)
        
        cropped = image[y:y+bh, x:x+bw]
        _, buffer = cv2.imencode('.jpg', cropped)
        return buffer.tobytes()

    def convert_to_jpeg(self, image_bytes: bytes) -> bytes:
        """Convert image to JPEG format"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()
```

---

## 10.2 Storage Utility

**File**: `app/utils/storage_util.py`

```python
import boto3
from botocore.client import Config
from typing import Optional
from app.configs.storage_config import storage_config
import os

class StorageUtil:
    def __init__(self):
        if storage_config.STORAGE_TYPE == "s3":
            self.s3_client = boto3.client(
                's3',
                endpoint_url=storage_config.S3_ENDPOINT_URL,
                aws_access_key_id=storage_config.S3_ACCESS_KEY,
                aws_secret_access_key=storage_config.S3_SECRET_KEY,
                config=Config(signature_version='s3v4'),
                region_name=storage_config.S3_REGION
            )
            self.bucket = storage_config.S3_BUCKET
        else:
            self.storage_path = storage_config.LOCAL_STORAGE_PATH
            os.makedirs(self.storage_path, exist_ok=True)

    def upload_image(self, image_bytes: bytes, key: str) -> str:
        """Upload image to storage"""
        if storage_config.STORAGE_TYPE == "s3":
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=image_bytes,
                ContentType='image/jpeg'
            )
            return self.get_image_url(key)
        else:
            file_path = os.path.join(self.storage_path, key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'wb') as f:
                f.write(image_bytes)
            return f"/storage/{key}"

    def get_image_url(self, key: str) -> str:
        """Get public URL for image"""
        if storage_config.STORAGE_TYPE == "s3":
            return f"{storage_config.S3_ENDPOINT_URL}/{storage_config.S3_BUCKET}/{key}"
        else:
            return f"/storage/{key}"

    def delete_image(self, key: str) -> bool:
        """Delete image from storage"""
        try:
            if storage_config.STORAGE_TYPE == "s3":
                self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            else:
                file_path = os.path.join(self.storage_path, key)
                if os.path.exists(file_path):
                    os.remove(file_path)
            return True
        except:
            return False
```

---

## 10.3 Stream Utility

**File**: `app/utils/stream_util.py`

```python
import cv2
import numpy as np
from typing import Optional, Generator
from app.configs.camera_config import camera_config

class StreamUtil:
    def __init__(self):
        pass

    def get_stream_url(self, rtsp_url: str) -> Optional[str]:
        """Get MJPEG stream URL for RTSP stream"""
        # This would typically return a proxy URL
        # For now, return the RTSP URL directly
        return rtsp_url

    def check_stream_health(self, rtsp_url: str) -> bool:
        """Check if RTSP stream is accessible"""
        try:
            cap = cv2.VideoCapture(rtsp_url)
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                return ret
            return False
        except:
            return False

    def stream_frames(self, rtsp_url: str) -> Generator[bytes, None, None]:
        """Generator that yields MJPEG frames from RTSP stream"""
        cap = cv2.VideoCapture(rtsp_url)
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, camera_config.MJPEG_QUALITY])
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        finally:
            cap.release()
```

---

# 11. Middleware

## 11.1 Auth Middleware (Update)

**File**: `app/middlewares/auth_middleware.py` (extend existing)

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from typing import Optional, Dict
from app.configs.app_config import app_config

security = HTTPBearer()

SECRET_KEY = app_config.SECRET_KEY
ALGORITHM = "HS256"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    """Get current user from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_websocket_token(token: str) -> Optional[Dict]:
    """Verify WebSocket token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return payload
    except JWTError:
        return None
```

---

## 11.2 File Upload Middleware

**File**: `app/middlewares/file_upload_middleware.py`

```python
from fastapi import HTTPException, status, UploadFile
from app.configs.storage_config import storage_config
from app.utils.image_util import ImageUtil

class FileUploadMiddleware:
    def __init__(self):
        self.image_util = ImageUtil()

    async def validate_image_upload(self, file: UploadFile) -> bytes:
        """Validate and process image upload"""
        # Check file type
        if file.content_type not in storage_config.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed types: {storage_config.ALLOWED_IMAGE_TYPES}"
            )
        
        # Read file
        image_bytes = await file.read()
        
        # Check file size
        if len(image_bytes) > storage_config.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {storage_config.MAX_IMAGE_SIZE} bytes"
            )
        
        # Validate image
        if not self.image_util.validate_image(image_bytes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file"
            )
        
        return image_bytes

file_upload_middleware = FileUploadMiddleware()
```

---

# 12. Testing Strategy

## 12.1 Unit Tests

**File**: `tests/test_vehicle_detection.py`

```python
import pytest
from unittest.mock import Mock, patch
from app.services.alpr_service import ALPRService
from app.schemas.vehicle_detection_schema import VehicleDetectionCreate

@pytest.fixture
def db_session():
    """Mock database session"""
    return Mock()

@pytest.fixture
def alpr_service(db_session):
    """ALPR service fixture"""
    return ALPRService(db_session)

def test_detect_plate(alpr_service):
    """Test plate detection"""
    # Mock image
    image_bytes = b"fake_image_data"
    
    # Mock detection result
    with patch.object(alpr_service, 'detect_plate') as mock_detect:
        mock_detect.return_value = {
            "plate_number": "BLA-123",
            "confidence": 98.2,
            "bbox": {"x": 0.32, "y": 0.55, "w": 0.36, "h": 0.14}
        }
        
        result = alpr_service.detect_plate(image_bytes)
        
        assert result["plate_number"] == "BLA-123"
        assert result["confidence"] == 98.2
        assert result["bbox"] is not None

def test_match_vehicle(alpr_service):
    """Test vehicle matching"""
    with patch.object(alpr_service.vehicle_repo, 'get_by_plate_number') as mock_get:
        mock_vehicle = Mock()
        mock_vehicle.id = "test-uuid"
        mock_get.return_value = mock_vehicle
        
        result = alpr_service.match_vehicle("BLA-123")
        
        assert result is not None
        assert result.id == "test-uuid"
```

---

## 12.2 Integration Tests

**File**: `tests/test_api_vehicle_detection.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_detect_vehicle():
    """Test vehicle detection API"""
    # Mock image file
    with open("tests/fixtures/test_plate.jpg", "rb") as f:
        response = client.post(
            "/api/vehicles/detect",
            files={"file": ("test_plate.jpg", f, "image/jpeg")},
            data={"camera_id": "test-camera-id"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "detection_id" in data
    assert "plate_number" in data

def test_get_vehicle_detections():
    """Test getting vehicle detections"""
    response = client.get("/api/vehicles/detections")
    
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
```

---

# 13. Main Application Update

**File**: `app/main.py` (update)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.di.container import init_container
from app.edge.http.routes import (
    auth_route,
    user_route,
    camera_route,
    vehicle_route,
    vehicle_detection_route,
    person_route,
    face_detection_route,
    alert_route,
    entry_log_route,
    health_route
)
from app.edge.socket import surveillance_socket_route

def create_app() -> FastAPI:
    app = FastAPI(
        title="Smart Surveillance Backend",
        description="AI-powered vehicle plate and facial recognition for society security",
        version="1.0.0"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://smart-entry-vision.lovable.app"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(auth_route.router)
    app.include_router(user_route.router)
    app.include_router(camera_route.router)
    app.include_router(vehicle_route.router)
    app.include_router(vehicle_detection_route.router)
    app.include_router(person_route.router)
    app.include_router(face_detection_route.router)
    app.include_router(alert_route.router)
    app.include_router(entry_log_route.router)
    app.include_router(health_route.router)
    
    # Include WebSocket
    app.include_router(surveillance_socket_route.router)
    
    # Initialize DI container
    init_container()
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

# 14. Environment Variables

**File**: `env.example` (update)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/smart_surveillance

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Storage
STORAGE_TYPE=s3
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET=smart-surveillance
S3_REGION=us-east-1

# AI Models
YOLO_VEHICLE_MODEL_PATH=models/yolo/vehicle.pt
YOLO_FACE_MODEL_PATH=models/yolo/face.pt
OCR_MODEL_PATH=models/ocr
ARCFACE_MODEL_PATH=models/arcface

# Detection Thresholds
YOLO_CONFIDENCE_THRESHOLD=0.5
OCR_CONFIDENCE_THRESHOLD=0.8
FACE_SIMILARITY_THRESHOLD=0.6
PLATE_CONFIDENCE_THRESHOLD=0.7
FACE_CONFIDENCE_THRESHOLD=0.7

# Camera Streams
STREAM_BUFFER_SIZE=1048576
STREAM_TIMEOUT=30
STREAM_HEALTH_CHECK_INTERVAL=60

# CORS
FRONTEND_URL=https://smart-entry-vision.lovable.app
```

---

# 15. Docker Configuration Updates

**File**: `docker-compose.yml` (update)

```yaml
version: '3.8'

services:
  backend:
    build: ...
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/smart_surveillance
      - S3_ENDPOINT_URL=http://minio:9000
      - S3_ACCESS_KEY=minioadmin
      - S3_SECRET_KEY=minioadmin
    depends_on:
      - db
      - minio

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=minioadmin
    volumes:
      - minio_data:/data

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=smart_surveillance
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  minio_data:
  postgres_data:
```

---

# Implementation Phases Summary

## Phase 1: Foundation (Week 1-2)
- Create all database migrations
- Implement base models and schemas
- Set up authentication system
- Create core utilities (image, storage, stream)

## Phase 2: User & Camera Management (Week 2-3)
- Implement user CRUD operations
- Implement camera CRUD operations
- Set up camera streaming infrastructure

## Phase 3: Vehicle Recognition (Week 3-5)
- Implement vehicle registration
- Implement vehicle detection with mock AI
- Set up vehicle detection API
- Integrate real YOLO + OCR models

## Phase 4: Face Recognition (Week 4-6)
- Implement person enrollment
- Implement face detection with mock AI
- Set up face detection API
- Integrate real YOLO-face + ArcFace models

## Phase 5: Alert System (Week 5-6)
- Implement alert generation logic
- Implement alert management API
- Set up alert WebSocket broadcasting

## Phase 6: Entry Logs & Analytics (Week 6)
- Implement entry log system
- Implement statistics endpoints
- Add search and filtering

## Phase 7: Real-time Features (Week 6-7)
- Implement WebSocket for live updates
- Set up camera streaming proxy
- Integrate event broadcasting

## Phase 8: Testing & Deployment (Week 7-8)
- Write unit tests
- Write integration tests
- Performance optimization
- Deployment setup

---

# Notes

- All models use UUID as primary keys
- All timestamps are in UTC
- Image storage uses S3/MinIO for scalability
- AI models can be swapped without changing service layer
- WebSocket authentication uses query parameter token
- CORS is configured for the Lovable frontend URL
- All API endpoints require authentication except health check
- Pagination is consistent across all list endpoints
- Error responses follow FastAPI standard format
