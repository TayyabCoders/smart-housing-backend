import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base
from app.models.enums import VisitorApprovalStatus


class VisitorApproval(Base):
    __tablename__ = "visitor_approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    face_detection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("face_detections.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    
    person_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("persons.id", ondelete="SET NULL"),
        nullable=True
    )
    
    status: Mapped[VisitorApprovalStatus] = mapped_column(
        SQLEnum(VisitorApprovalStatus, name="visitor_approval_status"),
        nullable=False,
        default=VisitorApprovalStatus.PENDING,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    
    decided_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Relationships
    face_detection = relationship("FaceDetection")
    person = relationship("Person")

    __table_args__ = (
        Index('ix_visitor_approvals_status_created', 'status', 'created_at'),
    )
