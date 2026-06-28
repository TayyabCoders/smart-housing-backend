from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from app.models.user_model import User

logger = get_logger(__name__)

class ComplaintController:
    @inject
    def __init__(self, complaint_mediator = Provide["complaint_mediator"]):
        self.complaint_mediator = complaint_mediator

    async def list_complaints(self, filters: dict = None, offset: int = 0, limit: int = 10, current_user: User = None):
        try:
            logger.info("ComplaintController: Listing complaints...")
            
            result = await self.complaint_mediator.list_complaints(filters, offset, limit, current_user)
            
            logger.info("ComplaintController: Listed complaints successfully.")
            
            return result 

        except Exception as e:
            logger.error("ComplaintController: Failed to list complaints.", exc_info=True)
            raise e

    async def get_complaint(self, complaint_id: str):
        try:
            logger.info("ComplaintController: Getting complaint...")
            
            complaint = await self.complaint_mediator.get_complaint(complaint_id)
            
            logger.info("ComplaintController: Got complaint successfully.")
            
            return complaint

        except Exception as e:
            logger.error("ComplaintController: Failed to get complaint.", exc_info=True)
            raise e

    async def get_complaint_by_tracking_id(self, tracking_id: str):
        try:
            logger.info("ComplaintController: Getting complaint by tracking_id...")
            
            complaint = await self.complaint_mediator.get_complaint_by_tracking_id(tracking_id)
            
            logger.info("ComplaintController: Got complaint successfully.")
            
            return complaint

        except Exception as e:
            logger.error("ComplaintController: Failed to get complaint by tracking_id.", exc_info=True)
            raise e

    async def create_complaint(self, complaint_data, current_user: User = None):
        try:
            logger.info("ComplaintController: Creating complaint...")
            
            complaint = await self.complaint_mediator.create_complaint(complaint_data, current_user)
            
            logger.info("ComplaintController: Created complaint successfully.")

            return complaint 

        except Exception as e:
            logger.error("ComplaintController: Failed to create complaint.", exc_info=True)
            raise e

    async def update_complaint(self, complaint_id: str, complaint_data, current_user: User = None):
        try:
            logger.info("ComplaintController: Updating complaint...")
            
            complaint = await self.complaint_mediator.update_complaint(complaint_id, complaint_data, current_user)
            
            logger.info("ComplaintController: Updated complaint successfully.")

            return complaint 

        except Exception as e:
            logger.error("ComplaintController: Failed to update complaint.", exc_info=True)
            raise e

    async def delete_complaint(self, complaint_id: str):
        try:
            logger.info("ComplaintController: Deleting complaint...")
            
            result = await self.complaint_mediator.delete_complaint(complaint_id)
            
            logger.info("ComplaintController: Deleted complaint successfully.")

            return result 

        except Exception as e:
            logger.error("ComplaintController: Failed to delete complaint.", exc_info=True)
            raise e
