from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models.election import Election

from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from typing import Any

logger = get_logger(__name__)

class ElectionRepository(BaseRepository[Election]):
    @inject
    def __init__(self, database = Provide["database"], cache : Optional[Any] = Provide["cache"]):
        super().__init__(Election, database, cache)

    async def findActiveElection(self) -> Optional[Election]:
        try:
            logger.info("ElectionRepository: Finding active election...")
            
            election = await self.findOne(filters={"is_active": True})
            
            logger.info("ElectionRepository: Found active election.")
            
            return election
        
        except Exception as e:
            logger.error("ElectionRepository: Failed to find active election.", exc_info=True)
            raise e
