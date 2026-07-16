"""
Face detection endpoints
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from dependency_injector.wiring import inject, Provide

from app.edge.http.controller.face_controller import FaceController
from app.middlewares.auth_middleware import get_current_user
from app.models.user_model import User
from app.schemas.face_detection_schema import (
    FaceDetectionResponse,
    FaceDetectionActionRequest,
    FaceDetectionListResponse,
)

router = APIRouter()


@router.post("/detect", response_model=FaceDetectionResponse)
@inject
async def detect_face(
    file: UploadFile = File(...),
    camera_id: UUID = Query(..., description="Camera ID for the detection"),
    current_user: User = Depends(get_current_user),
    controller: FaceController = Depends(Provide["face_controller"]),
):
    """Detect and match a face against enrolled residents/staff"""
    return await controller.detect_and_match(file, camera_id)


@router.post("/enroll")
@inject
async def enroll_face(
    file: UploadFile = File(...),
    person_id: Optional[UUID] = Form(None, description="Existing person to add another photo to"),
    name: Optional[str] = Form(None, description="Required when enrolling a new person"),
    role: Optional[str] = Form(None, description="resident | staff | visitor"),
    flat_no: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    controller: FaceController = Depends(Provide["face_controller"]),
):
    """Enroll a face embedding for a new or existing person"""
    return await controller.enroll(file, person_id, name, role, flat_no, phone)


@router.get("/detections", response_model=FaceDetectionListResponse)
@inject
async def list_face_detections(
    camera_id: Optional[UUID] = Query(None, description="Filter by camera ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to (ISO 8601)"),
    search: Optional[str] = Query(None, description="Search by person name"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
    current_user: User = Depends(get_current_user),
    controller: FaceController = Depends(Provide["face_controller"]),
):
    """List face detections with filters, pagination, and stats"""
    return await controller.list_detections(camera_id, status, date_from, date_to, search, offset, limit)


@router.post("/detections/{id}/action")
@inject
async def face_detection_action(
    id: UUID,
    action_request: FaceDetectionActionRequest,
    current_user: User = Depends(get_current_user),
    controller: FaceController = Depends(Provide["face_controller"]),
):
    """Apply action to face detection"""
    return await controller.apply_action(id, action_request.action, current_user.id)
