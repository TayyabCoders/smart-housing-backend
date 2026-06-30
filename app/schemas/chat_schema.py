from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID


class MessageCreate(BaseModel):
    receiver_id: UUID
    content: str


class MessageResponse(BaseModel):
    id: UUID
    sender_id: UUID
    receiver_id: UUID
    content: str
    timestamp: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


class ConversationResponse(BaseModel):
    id: UUID
    user_id: UUID
    username: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int
    is_online: bool

    model_config = ConfigDict(from_attributes=True)


class WebSocketMessage(BaseModel):
    type: str  # "message", "read_receipt", "typing"
    sender_id: UUID
    receiver_id: UUID
    content: Optional[str] = None
    timestamp: Optional[datetime] = None
