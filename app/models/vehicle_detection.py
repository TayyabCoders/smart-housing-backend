import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey, JSON, Numeric, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base
from app.models.enums import DetectionStatus, ActionType


class VehicleDetection(Base):
    __tablename__ = "vehicle_detections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    plate_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    
    matched_vehicle_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True
    )
    
    confidence: Mapped[Optional[float]] = mapped_column(Numeric(5, 4), nullable=True)
    
    bbox: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    camera_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    status: Mapped[DetectionStatus] = mapped_column(
        SQLEnum(DetectionStatus, name="detection_status"),
        nullable=False,
        default=DetectionStatus.UNKNOWN,
        index=True
    )
    
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    full_frame_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    action_taken: Mapped[Optional[ActionType]] = mapped_column(
        SQLEnum(ActionType, name="action_type"),
        nullable=True
    )
    
    acted_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    detected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    # Relationships
    camera = relationship("Camera", back_populates="vehicle_detections")
    matched_vehicle = relationship("Vehicle", back_populates="detections")
    acted_by_user = relationship("User", foreign_keys=[acted_by])

    __table_args__ = (
        Index('ix_vehicle_detections_camera_detected', 'camera_id', 'detected_at'),
        Index('ix_vehicle_detections_status_detected', 'status', 'detected_at'),
    )
