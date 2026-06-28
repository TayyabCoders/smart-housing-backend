from pydantic import BaseModel, ConfigDict


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    vehicles_today: int
    vehicles_yesterday_delta: int
    faces_verified: int
    faces_match_rate: float
    active_visitors: int
    visitors_awaiting_approval: int
    alerts_24h: int
    alerts_blacklist_count: int

    model_config = ConfigDict(from_attributes=True)
