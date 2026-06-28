"""
Face detection endpoints
"""
from uuid import UUID
from fastapi import APIRouter, UploadFile, File, Query

from app.schemas.face_detection_schema import (
    FaceDetectionResponse,
    FaceDetectionActionRequest,
    FaceDetectionListResponse,
)

router = APIRouter(prefix="/api/faces", tags=["face-detections"])


@router.post("/detect", response_model=FaceDetectionResponse)
async def detect_face(
    file: UploadFile = File(...),
    camera_id: UUID = Query(..., description="Camera ID for the detection")
):
    """Detect face from uploaded image - placeholder endpoint"""
    return {
        "id": UUID("00000000-0000-0000-0000-000000000000"),
        "matched_person_id": None,
        "confidence": 0.92,
        "bbox": {"x": 150, "y": 150, "width": 100, "height": 100},
        "status": "unknown",
        "image_url": None,
        "full_frame_url": None,
        "matched_person": None,
        "camera_name": None,
    }


@router.get("/detections", response_model=FaceDetectionListResponse)
async def list_face_detections(
    camera_id: UUID = Query(None, description="Filter by camera ID"),
    status: str = Query(None, description="Filter by status"),
    date_from: str = Query(None, description="Filter by date from (ISO 8601)"),
    date_to: str = Query(None, description="Filter by date to (ISO 8601)"),
    search: str = Query(None, description="Search by person name"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
):
    """List face detections with filters and pagination - placeholder endpoint"""
    return {
        "items": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
        "stats": None,
    }


@router.post("/detections/{id}/action")
async def face_detection_action(
    id: UUID,
    action_request: FaceDetectionActionRequest,
):
    """Apply action to face detection - placeholder endpoint"""
    return {
        "message": f"Action '{action_request.action}' applied to detection {id}",
        "status": "placeholder",
    }
