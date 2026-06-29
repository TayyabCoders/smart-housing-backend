import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base

class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id"),
        nullable=False
    )
    
    voter_name: Mapped[str] = mapped_column(String(255), nullable=False)
    voter_nic: Mapped[str] = mapped_column(String(15), unique=True, index=True, nullable=False)  # CNIC format: XXXXX-XXXXXXX-X
    voter_block: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    voter_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    voted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
