import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base
from app.models.enums import CameraType


class Camera(Base):
    __tablename__ = "cameras"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stream_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    type: Mapped[CameraType] = mapped_column(
        SQLEnum(CameraType, name="camera_type"),
        nullable=False,
        default=CameraType.BOTH
    )
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    vehicle_detections = relationship(
        "VehicleDetection",
        back_populates="camera",
        cascade="all, delete-orphan"
    )
    
    face_detections = relationship(
        "FaceDetection",
        back_populates="camera",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('ix_cameras_type_active', 'type', 'is_active'),
    )
