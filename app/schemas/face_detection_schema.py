from typing import Optional, Literal
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common_schema import PaginatedResponse


class MatchedPersonInfo(BaseModel):
    """Information about matched person"""
    name: Optional[str] = None
    flat_no: Optional[str] = None
    role: str

    model_config = ConfigDict(from_attributes=True)


class FaceDetectionResponse(BaseModel):
    """Face detection response"""
    id: UUID
    matched_person_id: Optional[UUID] = None
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0 and 1")
    bbox: Optional[dict] = None
    status: str
    image_url: Optional[str] = None
    full_frame_url: Optional[str] = None
    matched_person: Optional[MatchedPersonInfo] = None
    camera_name: Optional[str] = None
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FaceDetectionActionRequest(BaseModel):
    """Action request for face detection"""
    action: Literal["open_gate", "block", "allow", "deny", "flag_unknown", "register_visitor"]


class FaceDetectionListResponse(PaginatedResponse[FaceDetectionResponse]):
    """Paginated list of face detections with optional stats"""
    stats: Optional[dict] = None
