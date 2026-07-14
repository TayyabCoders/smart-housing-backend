from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from dependency_injector.wiring import inject, Provide

from app.models.parking_record_model import ParkingRecord
from app.repositories.base_repository import BaseRepository

logger = structlog.get_logger(__name__)


class ParkingRepository(BaseRepository):
    @inject
    def __init__(
        self,
        database=Provide["database"],
        cache=Provide["cache"],
    ):
        super().__init__(ParkingRecord, database, cache)

    async def find_active_by_plate(self, plate_number: str) -> Optional[ParkingRecord]:
        """Find the currently active (status=IN) record for a plate."""
        try:
            async with self.database.get_session("read") as session:
                stmt = (
                    select(ParkingRecord)
                    .where(
                        ParkingRecord.plate_number == plate_number,
                        ParkingRecord.status == "IN",
                    )
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error("ParkingRepository: find_active_by_plate failed", exc_info=True)
            raise e

    async def find_latest_by_plate(self, plate_number: str) -> Optional[ParkingRecord]:
        """Find the most recent record for a plate regardless of status."""
        try:
            async with self.database.get_session("read") as session:
                stmt = (
                    select(ParkingRecord)
                    .where(ParkingRecord.plate_number == plate_number)
                    .order_by(ParkingRecord.entry_time.desc())
                    .limit(1)
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error("ParkingRepository: find_latest_by_plate failed", exc_info=True)
            raise e

    async def find_paginated(
        self,
        page: int = 1,
        limit: int = 50,
        status_filter: Optional[str] = None,
        date_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Paginated list of parking records with optional filters."""
        try:
            async with self.database.get_session("read") as session:
                base_stmt = select(ParkingRecord)
                count_stmt = select(func.count()).select_from(ParkingRecord)

                if status_filter:
                    base_stmt = base_stmt.where(ParkingRecord.status == status_filter)
                    count_stmt = count_stmt.where(ParkingRecord.status == status_filter)

                if date_filter:
                    y, m, d = map(int, date_filter.split("-"))
                    date_iso = f"{y:04d}-{m:02d}-{d:02d}"
                    date_cond = func.to_char(ParkingRecord.entry_time, "YYYY-MM-DD") == date_iso
                    base_stmt = base_stmt.where(date_cond)
                    count_stmt = count_stmt.where(date_cond)

                total_result = await session.execute(count_stmt)
                total = total_result.scalar()

                data_stmt = (
                    base_stmt
                    .order_by(ParkingRecord.entry_time.desc())
                    .offset((page - 1) * limit)
                    .limit(limit)
                )
                items_result = await session.execute(data_stmt)
                items = list(items_result.scalars().all())

                return {"total": total, "items": items}
        except Exception as e:
            logger.error("ParkingRepository: find_paginated failed", exc_info=True)
            raise e

    async def create_record(self, data: Dict[str, Any]) -> ParkingRecord:
        """Insert a new parking record."""
        return await self.create(data)

    async def update_record(self, record_id: int, data: Dict[str, Any]) -> Optional[ParkingRecord]:
        """Update an existing parking record by id."""
        return await self.update(record_id, data)
