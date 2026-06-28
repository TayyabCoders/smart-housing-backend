from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from app.models.user_model import User

logger = get_logger(__name__)

class ComplaintMediator:
    @inject
    def __init__(
        self,
        complaint_service = Provide["complaint_service"]
    ):
        self.complaint_service = complaint_service

    async def list_complaints(self, filters: dict = None, offset: int = 0, limit: int = 10, current_user: User = None):
        try:
            logger.info("ComplaintMediator: Listing complaints...")
            
            result = await self.complaint_service.list_complaints(filters, offset, limit, current_user)
            
            logger.info("ComplaintMediator: Listed complaints successfully.")
            
            return result
        
        except Exception as e:
            logger.error("ComplaintMediator: Failed to list complaints.", exc_info=True)
            raise e

    async def get_complaint(self, complaint_id: str):
        try:
            logger.info("ComplaintMediator: Getting complaint...")
            
            result = await self.complaint_service.get_complaint(complaint_id)
            
            logger.info("ComplaintMediator: Got complaint successfully.")
            
            return result
        
        except Exception as e:
            logger.error("ComplaintMediator: Failed to get complaint.", exc_info=True)
            raise e

    async def get_complaint_by_tracking_id(self, tracking_id: str):
        try:
            logger.info("ComplaintMediator: Getting complaint by tracking_id...")
            
            result = await self.complaint_service.get_complaint_by_tracking_id(tracking_id)
            
            logger.info("ComplaintMediator: Got complaint successfully.")
            
            return result
        
        except Exception as e:
            logger.error("ComplaintMediator: Failed to get complaint by tracking_id.", exc_info=True)
            raise e

    async def create_complaint(self, complaint_data, current_user: User = None):
        try:
            logger.info("ComplaintMediator: Creating complaint...")
            
            complaint = await self.complaint_service.create_complaint(complaint_data, current_user)
            
            logger.info("ComplaintMediator: Complaint created successfully.")
            
            return complaint
        
        except Exception as e:
            logger.error("ComplaintMediator: Failed to create complaint.", exc_info=True)
            raise e

    async def update_complaint(self, complaint_id: str, complaint_data, current_user: User = None):
        try:
            logger.info("ComplaintMediator: Updating complaint...")
            
            complaint = await self.complaint_service.update_complaint(complaint_id, complaint_data, current_user)
            
            logger.info("ComplaintMediator: Complaint updated successfully.")
            
            return complaint
        
        except Exception as e:
            logger.error("ComplaintMediator: Failed to update complaint.", exc_info=True)
            raise e

    async def delete_complaint(self, complaint_id: str):
        try:
            logger.info("ComplaintMediator: Deleting complaint...")
            
            result = await self.complaint_service.delete_complaint(complaint_id)
            
            logger.info("ComplaintMediator: Complaint deleted successfully.")
            
            return result
        
        except Exception as e:
            logger.error("ComplaintMediator: Failed to delete complaint.", exc_info=True)
            raise e
