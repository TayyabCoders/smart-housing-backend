from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CameraResponse(BaseModel):
    """Camera response"""
    id: UUID
    code: str
    name: str
    location: Optional[str] = None
    stream_url: Optional[str] = None
    type: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CameraCreateRequest(BaseModel):
    """Request to create a camera"""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    stream_url: Optional[str] = Field(None, max_length=500)
    type: str
    is_active: bool = True


class CameraUpdateRequest(BaseModel):
    """Request to update a camera"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    location: Optional[str] = Field(None, max_length=255)
    stream_url: Optional[str] = Field(None, max_length=500)
    type: Optional[str] = None
    is_active: Optional[bool] = None
