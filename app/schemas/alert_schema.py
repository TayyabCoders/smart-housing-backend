from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

from app.schemas.common_schema import PaginatedResponse


class AlertVehicleDetectionInfo(BaseModel):
    """Vehicle detection info in alert"""
    plate: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AlertFaceDetectionInfo(BaseModel):
    """Face detection info in alert"""
    person_name: Optional[str] = None
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AlertResponse(BaseModel):
    """Alert response"""
    id: UUID
    kind: str
    severity: str
    title: str
    description: Optional[str] = None
    camera_name: Optional[str] = None
    vehicle_detection: Optional[AlertVehicleDetectionInfo] = None
    face_detection: Optional[AlertFaceDetectionInfo] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertDismissRequest(BaseModel):
    """Request to dismiss an alert"""
    pass


class AlertResolveRequest(BaseModel):
    """Request to resolve an alert"""
    pass


class AlertListResponse(PaginatedResponse[AlertResponse]):
    """Paginated list of alerts"""
