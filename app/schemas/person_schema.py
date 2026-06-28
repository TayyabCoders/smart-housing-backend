from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class PersonResponse(BaseModel):
    """Person response"""
    id: UUID
    name: str
    role: str
    flat_no: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: bool
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    embeddings_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PersonCreateRequest(BaseModel):
    """Request to create a person"""
    name: str = Field(..., min_length=1, max_length=255)
    role: str
    flat_no: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None


class PersonUpdateRequest(BaseModel):
    """Request to update a person"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    role: Optional[str] = None
    flat_no: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    photo_url: Optional[str] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
