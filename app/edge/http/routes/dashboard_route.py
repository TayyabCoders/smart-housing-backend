"""
Dashboard endpoints
"""
from fastapi import APIRouter, Depends

from app.schemas.dashboard_schema import DashboardStatsResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats():
    """Get dashboard statistics - placeholder endpoint"""
    return {
        "vehicles_today": 0,
        "vehicles_yesterday_delta": 0,
        "faces_verified": 0,
        "faces_match_rate": 0.0,
        "active_visitors": 0,
        "visitors_awaiting_approval": 0,
        "alerts_24h": 0,
        "alerts_blacklist_count": 0,
    }
