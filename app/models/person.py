import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base
from app.models.enums import PersonRole


class Person(Base):
    __tablename__ = "persons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    
    role: Mapped[PersonRole] = mapped_column(
        SQLEnum(PersonRole, name="person_role"),
        nullable=False,
        default=PersonRole.RESIDENT,
        index=True
    )
    
    flat_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True
    )
    
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Relationships
    face_embeddings = relationship(
        "FaceEmbedding",
        back_populates="person",
        cascade="all, delete-orphan"
    )
    
    face_detections = relationship(
        "FaceDetection",
        back_populates="matched_person",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('ix_persons_role_active', 'role', 'is_active'),
        Index('ix_persons_validity', 'valid_from', 'valid_until'),
    )
