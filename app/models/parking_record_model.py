import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base_model import Base


class ParkingRecord(Base):
    __tablename__ = "parking_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    plate_number: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    cnic_number: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    entry_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    exit_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    fee: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    entry_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    exit_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="IN")  # IN | OUT
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


Index("ix_parking_plate_status", ParkingRecord.plate_number, ParkingRecord.status)
Index("ix_parking_entry_time", ParkingRecord.entry_time)
Index("ix_parking_cnic", ParkingRecord.cnic_number)
