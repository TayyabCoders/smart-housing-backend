"""
Announcement endpoints
"""
from fastapi import APIRouter, Depends, Query
from app.schemas.announcement_schema import AnnouncementCreate, AnnouncementUpdate, Announcement
from app.edge.http.controller.announcement_controller import AnnouncementController
from app.di.container import container
from app.middlewares.auth_middleware import get_current_user, require_admin
from app.models.user_model import User
from dependency_injector.wiring import inject, Provide

router = APIRouter()


@router.get("/", response_model=dict)
@inject
async def list_announcements(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    announcement_controller: AnnouncementController = Depends(Provide["announcement_controller"])
):
    """List announcements with pagination. Any authenticated user can view."""
    return await announcement_controller.list_announcements(offset=offset, limit=limit)


@router.get("/{announcement_id}", response_model=Announcement)
@inject
async def get_announcement(
    announcement_id: str,
    current_user: User = Depends(get_current_user),
    announcement_controller: AnnouncementController = Depends(Provide["announcement_controller"])
):
    """Get announcement by ID. Any authenticated user can view."""
    return await announcement_controller.get_announcement(announcement_id)


@router.post("/", response_model=Announcement)
@inject
async def create_announcement(
    announcement_data: AnnouncementCreate,
    current_user: User = Depends(require_admin),
    announcement_controller: AnnouncementController = Depends(Provide["announcement_controller"])
):
    """Create a new announcement. Admin only."""
    return await announcement_controller.create_announcement(announcement_data, current_user)


@router.put("/{announcement_id}", response_model=Announcement)
@inject
async def update_announcement(
    announcement_id: str,
    announcement_data: AnnouncementUpdate,
    _ = Depends(require_admin),
    announcement_controller: AnnouncementController = Depends(Provide["announcement_controller"])
):
    """Update announcement by ID. Admin only."""
    return await announcement_controller.update_announcement(announcement_id, announcement_data)


@router.delete("/{announcement_id}")
@inject
async def delete_announcement(
    announcement_id: str,
    _ = Depends(require_admin),
    announcement_controller: AnnouncementController = Depends(Provide["announcement_controller"])
):
    """Delete announcement by ID. Admin only."""
    return await announcement_controller.delete_announcement(announcement_id)
