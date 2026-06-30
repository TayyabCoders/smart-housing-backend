import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, Boolean, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from app.models.base_model import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    sender_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    sender: Mapped["User"] = relationship("User", foreign_keys=[sender_id])
    receiver: Mapped["User"] = relationship("User", foreign_keys=[receiver_id])


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    user1_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    user2_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False
    )
    
    last_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    last_message_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    
    unread_count_user1: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    unread_count_user2: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user1: Mapped["User"] = relationship("User", foreign_keys=[user1_id])
    user2: Mapped["User"] = relationship("User", foreign_keys=[user2_id])
