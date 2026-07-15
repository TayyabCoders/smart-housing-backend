from datetime import datetime, timezone
from typing import Any, Dict, List

import structlog
from dependency_injector.wiring import inject, Provide
from sqlalchemy import func, select

from app.models.access_log import AccessLog
from app.repositories.base_repository import BaseRepository

logger = structlog.get_logger(__name__)


class AccessLogRepository(BaseRepository):
    @inject
    def __init__(self, database=Provide["database"], cache=Provide["cache"]):
        super().__init__(AccessLog, database, cache)

    async def create_log(self, data: Dict[str, Any]) -> AccessLog:
        return await self.create(data)

    async def find_recent(self, limit: int = 50) -> List[AccessLog]:
        try:
            async with self.database.get_session("read") as session:
                stmt = (
                    select(AccessLog)
                    .order_by(AccessLog.accessed_at.desc())
                    .limit(limit)
                )
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            logger.error("AccessLogRepository: find_recent failed", exc_info=True)
            raise e

    async def find_today_stats(self) -> Dict[str, int]:
        """Return counts grouped by vehicle_status for today."""
        try:
            today_start = datetime.now(timezone.utc).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            async with self.database.get_session("read") as session:
                stmt = (
                    select(AccessLog.vehicle_status, func.count(AccessLog.id))
                    .where(AccessLog.accessed_at >= today_start)
                    .group_by(AccessLog.vehicle_status)
                )
                result = await session.execute(stmt)
                rows = result.all()

            counts: Dict[str, int] = {row[0]: row[1] for row in rows}
            total = sum(counts.values())

            return {
                "detected_today": total,
                "residents": counts.get("resident", 0),
                "visitors": counts.get("visitor", 0),
                "staff": counts.get("staff", 0),
                "blacklist_hits": counts.get("blacklist", 0),
                "unknown": counts.get("unknown", 0),
            }
        except Exception as e:
            logger.error("AccessLogRepository: find_today_stats failed", exc_info=True)
            raise e
