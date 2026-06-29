from pydantic import BaseModel, ConfigDict


class Metrics(BaseModel):
    """Dashboard metrics"""
    totalUsers: int
    totalComplaints: int
    pendingComplaints: int
    totalVoters: int

    model_config = ConfigDict(from_attributes=True)


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response"""
    success: bool
    data: dict

    model_config = ConfigDict(from_attributes=True)
