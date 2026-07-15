from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel

router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class AccessRequest(BaseModel):
    plate_number: str
    vehicle_status: str        # resident | visitor | staff | blacklist | unknown
    owner_name: Optional[str] = None
    flat_no: Optional[str] = None
    snapshot_url: Optional[str] = None


class AccessLogResponse(BaseModel):
    id: int
    plate_number: str
    vehicle_status: str
    action: str
    owner_name: Optional[str] = None
    flat_no: Optional[str] = None
    snapshot_url: Optional[str] = None
    accessed_at: datetime

    class Config:
        from_attributes = True


class TodayStatsResponse(BaseModel):
    detected_today: int
    residents: int
    visitors: int
    staff: int
    blacklist_hits: int
    unknown: int


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/grant", response_model=AccessLogResponse, status_code=201)
@inject
async def grant_access(
    body: AccessRequest,
    access_log_repository=Depends(Provide["access_log_repository"]),
):
    """Record a GRANTED access event (gate opened)."""
    log = await access_log_repository.create_log({
        "plate_number": body.plate_number.upper().strip(),
        "vehicle_status": body.vehicle_status,
        "action": "GRANTED",
        "owner_name": body.owner_name,
        "flat_no": body.flat_no,
        "snapshot_url": body.snapshot_url,
        "accessed_at": datetime.now(timezone.utc),
    })
    return log


@router.post("/deny", response_model=AccessLogResponse, status_code=201)
@inject
async def deny_access(
    body: AccessRequest,
    access_log_repository=Depends(Provide["access_log_repository"]),
):
    """Record a DENIED access event (vehicle blocked)."""
    log = await access_log_repository.create_log({
        "plate_number": body.plate_number.upper().strip(),
        "vehicle_status": body.vehicle_status,
        "action": "DENIED",
        "owner_name": body.owner_name,
        "flat_no": body.flat_no,
        "snapshot_url": body.snapshot_url,
        "accessed_at": datetime.now(timezone.utc),
    })
    return log


@router.get("/recent", response_model=List[AccessLogResponse])
@inject
async def get_recent(
    limit: int = 50,
    access_log_repository=Depends(Provide["access_log_repository"]),
):
    """Return the most recent access events."""
    logs = await access_log_repository.find_recent(limit=min(limit, 200))
    return logs


@router.get("/stats/today", response_model=TodayStatsResponse)
@inject
async def get_today_stats(
    access_log_repository=Depends(Provide["access_log_repository"]),
):
    """Return today's access counts grouped by vehicle status."""
    stats = await access_log_repository.find_today_stats()
    return TodayStatsResponse(**stats)
