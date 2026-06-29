from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models.activity_log import ActivityLog

from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from typing import Any

logger = get_logger(__name__)

class ActivityLogRepository(BaseRepository[ActivityLog]):
    @inject
    def __init__(self, database = Provide["database"], cache : Optional[Any] = Provide["cache"]):
        super().__init__(ActivityLog, database, cache)

    async def findRecentLogs(self, limit: int = 15) -> list[ActivityLog]:
        try:
            logger.info("ActivityLogRepository: Finding recent activity logs...")
            
            # Use findAndCountAll with limit to get recent logs
            result = await self.findAndCountAll(offset=0, limit=limit)
            
            logger.info("ActivityLogRepository: Found recent activity logs.")
            
            return result["rows"]
        
        except Exception as e:
            logger.error("ActivityLogRepository: Failed to find recent activity logs.", exc_info=True)
            raise e
