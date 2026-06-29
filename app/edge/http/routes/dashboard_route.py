"""
Dashboard endpoints
"""
from fastapi import APIRouter, Depends
from app.edge.http.controller.dashboard_controller import DashboardController
from app.di.container import container
from dependency_injector.wiring import inject, Provide

router = APIRouter()


@router.get("/")
@inject
async def get_dashboard_stats(
    dashboard_controller: DashboardController = Depends(Provide["dashboard_controller"])
):
    """Get dashboard statistics"""
    return await dashboard_controller.get_dashboard_metrics()
