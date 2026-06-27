import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base
from app.models.enums import AlertKind, AlertSeverity, AlertStatus


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    kind: Mapped[AlertKind] = mapped_column(
        SQLEnum(AlertKind, name="alert_kind"),
        nullable=False,
        index=True
    )
    
    severity: Mapped[AlertSeverity] = mapped_column(
        SQLEnum(AlertSeverity, name="alert_severity"),
        nullable=False,
        index=True
    )
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    camera_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    
    vehicle_detection_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vehicle_detections.id", ondelete="SET NULL"),
        nullable=True
    )
    
    face_detection_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("face_detections.id", ondelete="SET NULL"),
        nullable=True
    )
    
    status: Mapped[AlertStatus] = mapped_column(
        SQLEnum(AlertStatus, name="alert_status"),
        nullable=False,
        default=AlertStatus.OPEN,
        index=True
    )
    
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )

    # Relationships
    camera = relationship("Camera")
    vehicle_detection = relationship("VehicleDetection")
    face_detection = relationship("FaceDetection")
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])

    __table_args__ = (
        Index('ix_alerts_status_created', 'status', 'created_at'),
        Index('ix_alerts_kind_created', 'kind', 'created_at'),
    )
