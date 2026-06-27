import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base
from app.models.enums import VehicleStatus


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    plate_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    owner_name: Mapped[str] = mapped_column(String(255), nullable=False)
    flat_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    vehicle_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    status: Mapped[VehicleStatus] = mapped_column(
        SQLEnum(VehicleStatus, name="vehicle_status"),
        nullable=False,
        default=VehicleStatus.RESIDENT,
        index=True
    )
    
    notes: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Relationships
    owner = relationship("User", foreign_keys=[owner_id])
    detections = relationship(
        "VehicleDetection",
        back_populates="matched_vehicle",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('ix_vehicles_status_flat', 'status', 'flat_no'),
    )
