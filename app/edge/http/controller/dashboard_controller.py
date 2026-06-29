from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger

logger = get_logger(__name__)


class DashboardController:
    @inject
    def __init__(
        self,
        dashboard_mediator = Provide["dashboard_mediator"]
    ):
        self.dashboard_mediator = dashboard_mediator

    async def get_dashboard_metrics(self):
        """Get dashboard statistics including total users, complaints, pending complaints, and total voters"""
        try:
            logger.info("DashboardController: Getting dashboard metrics...")
            
            result = await self.dashboard_mediator.get_dashboard_metrics()
            
            logger.info("DashboardController: Retrieved dashboard metrics successfully.")
            
            return result

        except Exception as e:
            logger.error("DashboardController: Failed to get dashboard metrics.", exc_info=True)
            raise e
