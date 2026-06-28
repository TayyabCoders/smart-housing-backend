from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models.complaint_model import Complaint

from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from typing import Any

logger = get_logger(__name__)

class ComplaintRepository(BaseRepository[Complaint]):
    @inject
    def __init__(self, database = Provide["database"], cache : Optional[Any] = Provide["cache"]):
        super().__init__(Complaint, database, cache)

    async def findByTrackingId(self, tracking_id: str) -> Optional[Complaint]:
        try:
            logger.info("ComplaintRepository: Finding complaint by tracking_id...")
            
            complaint = await self.findOne(filters={"tracking_id": tracking_id})
            
            logger.info("ComplaintRepository: Found complaint by tracking_id.")
            
            return complaint
        
        except Exception as e:
            logger.error("ComplaintRepository: Failed to find complaint by tracking_id.", exc_info=True)
            raise e
