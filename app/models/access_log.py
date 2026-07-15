from datetime import datetime
from typing import Optional

from sqlalchemy import String, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base_model import Base


class AccessLog(Base):
    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    plate_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    vehicle_status: Mapped[str] = mapped_column(String(20), nullable=False)  # resident/visitor/staff/blacklist/unknown
    action: Mapped[str] = mapped_column(String(20), nullable=False)          # GRANTED/DENIED
    owner_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    flat_no: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    snapshot_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    accessed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )


Index("ix_access_logs_status_accessed", AccessLog.vehicle_status, AccessLog.accessed_at)
Index("ix_access_logs_action_accessed", AccessLog.action, AccessLog.accessed_at)
