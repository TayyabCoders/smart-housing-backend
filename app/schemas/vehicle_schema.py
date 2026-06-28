from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class VehicleResponse(BaseModel):
    """Vehicle response"""
    id: UUID
    plate_number: str
    owner_id: Optional[UUID] = None
    owner_name: Optional[str] = None
    flat_no: Optional[str] = None
    vehicle_type: Optional[str] = None
    color: Optional[str] = None
    status: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class VehicleCreateRequest(BaseModel):
    """Request to create a vehicle"""
    plate_number: str = Field(..., min_length=1, max_length=20)
    owner_name: Optional[str] = Field(None, max_length=255)
    flat_no: Optional[str] = Field(None, max_length=50)
    vehicle_type: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=50)
    status: str
    notes: Optional[str] = Field(None, max_length=500)


class VehicleUpdateRequest(BaseModel):
    """Request to update a vehicle"""
    owner_name: Optional[str] = Field(None, max_length=255)
    flat_no: Optional[str] = Field(None, max_length=50)
    vehicle_type: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)
