import uuid
import random
import string
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, DateTime, Enum as SQLEnum, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base
from app.models.enums import ComplaintGender, ComplaintStatus

class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False
    )
    
    fullname: Mapped[str] = mapped_column(String(255), nullable=False)
    
    gender: Mapped[ComplaintGender] = mapped_column(
        SQLEnum(ComplaintGender, name="complaint_gender"), 
        nullable=False
    )
    
    complaint_detail: Mapped[str] = mapped_column(Text, nullable=False)
    
    tracking_id: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    
    status: Mapped[ComplaintStatus] = mapped_column(
        SQLEnum(ComplaintStatus, name="complaint_status"), 
        nullable=False,
        default=ComplaintStatus.Pending
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        onupdate=func.now()
    )

    @staticmethod
    def generate_tracking_id() -> str:
        """Generate a unique tracking ID in format CMP-XXXXXX where X is random alphanumeric (uppercase)"""
        # Generate 6 random characters (uppercase letters and numbers)
        characters = string.ascii_uppercase + string.digits
        random_part = ''.join(random.choices(characters, k=6))
        return f"CMP-{random_part}"
