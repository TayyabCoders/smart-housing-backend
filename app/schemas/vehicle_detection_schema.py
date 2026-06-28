from typing import Optional, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common_schema import PaginatedResponse


class MatchedVehicleInfo(BaseModel):
    """Information about matched vehicle"""
    owner_name: Optional[str] = None
    flat_no: Optional[str] = None
    vehicle_type: Optional[str] = None
    color: Optional[str] = None
    status: str

    model_config = ConfigDict(from_attributes=True)


class VehicleDetectionResponse(BaseModel):
    """Vehicle detection response"""
    id: UUID
    plate_number: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    bbox: Optional[dict] = None
    status: str
    image_url: Optional[str] = None
    full_frame_url: Optional[str] = None
    matched_vehicle: Optional[MatchedVehicleInfo] = None
    camera_name: Optional[str] = None
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleDetectionActionRequest(BaseModel):
    """Action request for vehicle detection"""
    action: Literal["open_gate", "block", "mark_visitor"]


class VehicleDetectionListResponse(PaginatedResponse[VehicleDetectionResponse]):
    """Paginated list of vehicle detections with optional stats"""
    stats: Optional[dict] = None
