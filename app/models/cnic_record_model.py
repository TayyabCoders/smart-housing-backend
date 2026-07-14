import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base_model import Base


class CnicRecord(Base):
    __tablename__ = "cnic_records"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    cnic_number: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    father_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gender: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country_of_stay: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    date_of_issue: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    date_of_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


Index("ix_cnic_number", CnicRecord.cnic_number)
Index("ix_cnic_name_dob", CnicRecord.name, CnicRecord.date_of_birth)
