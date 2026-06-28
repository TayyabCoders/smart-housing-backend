"""
Alert endpoints
"""
from uuid import UUID
from fastapi import APIRouter, Query

from app.schemas.alert_schema import (
    AlertResponse,
    AlertDismissRequest,
    AlertResolveRequest,
    AlertListResponse,
)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    kind: str = Query(None, description="Filter by alert kind"),
    severity: str = Query(None, description="Filter by severity"),
    status: str = Query(None, description="Filter by status"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Pagination limit"),
):
    """List alerts with filters and pagination - placeholder endpoint"""
    return {
        "items": [],
        "total": 0,
        "limit": limit,
        "offset": offset,
    }


@router.post("/{id}/dismiss")
async def dismiss_alert(id: UUID):
    """Dismiss an alert - placeholder endpoint"""
    return {
        "message": f"Alert {id} dismissed",
        "status": "placeholder",
    }


@router.post("/{id}/resolve")
async def resolve_alert(id: UUID):
    """Resolve an alert - placeholder endpoint"""
    return {
        "message": f"Alert {id} resolved",
        "status": "placeholder",
    }
