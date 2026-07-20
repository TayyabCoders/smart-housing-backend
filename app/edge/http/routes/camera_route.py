from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from sqlalchemy import select

from app.models.camera import Camera
from app.models.enums import CameraType

router = APIRouter()


class CameraResponse(BaseModel):
    id: str
    code: str
    name: str
    location: Optional[str] = None
    stream_url: Optional[str] = None
    type: str
    is_active: bool

    class Config:
        from_attributes = True


@router.get("", response_model=List[CameraResponse])
@inject
async def list_cameras(
    type: Optional[str] = Query(None, description="Filter by type: plate | face | both"),
    active_only: bool = Query(True),
    camera_repository=Depends(Provide["camera_repository"]),
):
    """Return cameras, optionally filtered by type."""
    if type:
        try:
            camera_type = CameraType(type.lower())
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid type. Must be one of: {[e.value for e in CameraType]}",
            )
        cameras = await camera_repository.find_by_type(camera_type, active_only=active_only)
    else:
        async with camera_repository.database.get_session("read") as session:
            stmt = select(Camera)
            if active_only:
                stmt = stmt.where(Camera.is_active.is_(True))
            stmt = stmt.order_by(Camera.created_at.asc())
            result = await session.execute(stmt)
            cameras = list(result.scalars().all())

    return [
        CameraResponse(
            id=str(c.id),
            code=c.code,
            name=c.name,
            location=c.location,
            stream_url=c.stream_url,
            type=c.type.value,
            is_active=c.is_active,
        )
        for c in cameras
    ]
