from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger

logger = get_logger(__name__)


class DashboardMediator:
    @inject
    def __init__(
        self,
        user_service = Provide["user_service"],
        complaint_service = Provide["complaint_service"],
        vote_service = Provide["vote_service"]
    ):
        self.user_service = user_service
        self.complaint_service = complaint_service
        self.vote_service = vote_service

    async def get_dashboard_metrics(self):
        try:
            logger.info("DashboardMediator: Getting dashboard metrics...")
            
            # Get total users
            users_result = await self.user_service.list_users(limit=1)
            total_users = users_result.get('total', 0)
            
            # Get total complaints and pending complaints
            complaints_result = await self.complaint_service.list_complaints(limit=1)
            total_complaints = complaints_result.get('total', 0)
            pending_complaints = complaints_result.get('pending', 0)
            
            # Get total voters
            votes_result = await self.vote_service.list_votes(limit=1)
            total_voters = votes_result.get('total', 0)
            
            metrics = {
                "totalUsers": total_users,
                "totalComplaints": total_complaints,
                "pendingComplaints": pending_complaints,
                "totalVoters": total_voters
            }
            
            logger.info("DashboardMediator: Retrieved dashboard metrics successfully.", metrics=metrics)
            
            return {
                "success": True,
                "data": {
                    "metrics": metrics
                }
            }
        
        except Exception as e:
            logger.error("DashboardMediator: Failed to get dashboard metrics.", exc_info=True)
            raise e
