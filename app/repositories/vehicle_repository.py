from typing import List, Optional

import structlog
from dependency_injector.wiring import inject, Provide

from app.models.vehicle import Vehicle
from app.repositories.base_repository import BaseRepository

logger = structlog.get_logger(__name__)


class VehicleRepository(BaseRepository):
    @inject
    def __init__(
        self,
        database=Provide["database"],
        cache=Provide["cache"],
    ):
        super().__init__(Vehicle, database, cache)

    async def find_by_plate(self, plate_number: str) -> Optional[Vehicle]:
        """Find a registered vehicle by plate number (case-insensitive)."""
        try:
            from sqlalchemy import select, func
            async with self.database.get_session("read") as session:
                stmt = select(Vehicle).where(
                    func.upper(Vehicle.plate_number) == plate_number.upper().strip()
                )
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error("VehicleRepository: find_by_plate failed", exc_info=True)
            raise e

    async def get_all_vehicles(self) -> List[Vehicle]:
        """Return all registered vehicles ordered by owner name."""
        try:
            from sqlalchemy import select
            async with self.database.get_session("read") as session:
                stmt = select(Vehicle).order_by(Vehicle.owner_name)
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            logger.error("VehicleRepository: get_all_vehicles failed", exc_info=True)
            raise e

    async def register_vehicle(self, data: dict) -> Vehicle:
        """Insert a new vehicle record."""
        return await self.create(data)

    async def update_status_by_plate(self, plate_number: str, status: str) -> Optional[Vehicle]:
        """Update the status of a vehicle by plate number."""
        try:
            vehicle = await self.find_by_plate(plate_number)
            if not vehicle:
                return None
            return await self.update(vehicle.id, {"status": status})
        except Exception as e:
            logger.error("VehicleRepository: update_status_by_plate failed", exc_info=True)
            raise e

    async def upsert_vehicle(self, plate_number: str, data: dict) -> Vehicle:
        """Create if not exists, otherwise update status and owner info."""
        try:
            vehicle = await self.find_by_plate(plate_number)
            if vehicle:
                return await self.update(vehicle.id, data)
            data["plate_number"] = plate_number.upper().strip()
            return await self.create(data)
        except Exception as e:
            logger.error("VehicleRepository: upsert_vehicle failed", exc_info=True)
            raise e

    async def delete_by_plate(self, plate_number: str) -> bool:
        """Remove a vehicle registration by plate number."""
        try:
            vehicle = await self.find_by_plate(plate_number)
            if not vehicle:
                return False
            return await self.delete(vehicle.id)
        except Exception as e:
            logger.error("VehicleRepository: delete_by_plate failed", exc_info=True)
            raise e
