"""
Complaint endpoints
"""
from fastapi import APIRouter, Depends, Query
from app.schemas.complaint_schema import ComplaintCreate, ComplaintUpdate, Complaint
from app.edge.http.controller.complaint_controller import ComplaintController
from app.di.container import container
from app.middlewares.auth_middleware import get_current_user
from app.models.user_model import User
from dependency_injector.wiring import inject, Provide

router = APIRouter()


@router.get("/", response_model=dict)
@inject
async def list_complaints(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    complaint_controller: ComplaintController = Depends(Provide["complaint_controller"])
):
    """List complaints with pagination. Users can only see their own complaints, admins can see all."""
    return await complaint_controller.list_complaints(offset=offset, limit=limit, current_user=current_user)


@router.get("/{complaint_id}", response_model=Complaint)
@inject
async def get_complaint(
    complaint_id: str,
    complaint_controller: ComplaintController = Depends(Provide["complaint_controller"])
):
    """Get complaint by ID"""
    return await complaint_controller.get_complaint(complaint_id)


@router.get("/tracking/{tracking_id}", response_model=Complaint)
@inject
async def get_complaint_by_tracking_id(
    tracking_id: str,
    complaint_controller: ComplaintController = Depends(Provide["complaint_controller"])
):
    """Get complaint by tracking ID"""
    return await complaint_controller.get_complaint_by_tracking_id(tracking_id)


@router.post("/", response_model=Complaint)
@inject
async def create_complaint(
    complaint_data: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    complaint_controller: ComplaintController = Depends(Provide["complaint_controller"])
):
    """Create a new complaint"""
    return await complaint_controller.create_complaint(complaint_data, current_user)


@router.put("/{complaint_id}", response_model=Complaint)
@inject
async def update_complaint(
    complaint_id: str,
    complaint_data: ComplaintUpdate,
    current_user: User = Depends(get_current_user),
    complaint_controller: ComplaintController = Depends(Provide["complaint_controller"])
):
    """Update complaint by ID. Admins can update any complaint, users can only update their own."""
    return await complaint_controller.update_complaint(complaint_id, complaint_data, current_user)


@router.delete("/{complaint_id}")
@inject
async def delete_complaint(
    complaint_id: str,
    complaint_controller: ComplaintController = Depends(Provide["complaint_controller"])
):
    """Delete complaint by ID"""
    return await complaint_controller.delete_complaint(complaint_id)
