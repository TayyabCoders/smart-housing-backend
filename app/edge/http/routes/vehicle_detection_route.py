"""
Vehicle detection endpoints
"""
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Query

from app.schemas.vehicle_detection_schema import (
    VehicleDetectionResponse,
    VehicleDetectionActionRequest,
    VehicleDetectionListResponse,
)

router = APIRouter(prefix="/api/vehicles", tags=["vehicle-detections"])


@router.post("/detect", response_model=VehicleDetectionResponse)
async def detect_vehicle(
    file: UploadFile = File(...),
    camera_id: UUID = Query(..., description="Camera ID for the detection")
):
    """Detect vehicle from uploaded image - placeholder endpoint"""
    return {
        "id": UUID("00000000-0000-0000-0000-000000000000"),
        "plate_number": "ABC123",
        "confidence": 0.95,
        "bbox": {"x": 100, "y": 100, "width": 200, "height": 100},
        "status": "unknown",
        "image_url": None,
        "full_frame_url": None,
        "matched_vehicle": None,
        "camera_name": None,
    }


@router.get("/detections", response_model=VehicleDetectionListResponse)
async def list_vehicle_detections(
    camera_id: UUID = Query(None, description="Filter by camera ID"),
    status: str = Query(None, description="Filter by status"),
    date_from: str = Query(None, description="Filter by date from (ISO 8601)"),
    date_to: str = Query(None, description="Filter by date to (ISO 8601)"),
    search: str = Query(None, description="Search by plate number"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
):
    """List vehicle detections with filters and pagination - placeholder endpoint"""
    return {
        "items": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "stats": None,
    }


@router.post("/detections/{id}/action")
async def vehicle_detection_action(
    id: UUID,
    action_request: VehicleDetectionActionRequest,
):
    """Apply action to vehicle detection - placeholder endpoint"""
    return {
        "message": f"Action '{action_request.action}' applied to detection {id}",
        "status": "placeholder",
    }
