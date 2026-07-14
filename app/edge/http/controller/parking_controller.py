from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class ParkingController:
    @inject
    def __init__(
        self,
        parking_mediator=Provide["parking_mediator"],
    ):
        self.parking_mediator = parking_mediator

    async def register_entry(self, upload_dir: Path, **kwargs) -> Dict[str, Any]:
        try:
            logger.info("ParkingController: register_entry")
            return await self.parking_mediator.register_entry(upload_dir, **kwargs)
        except Exception as e:
            logger.error("ParkingController: register_entry failed", exc_info=True)
            raise e

    async def register_exit(self, upload_dir: Path, **kwargs) -> Dict[str, Any]:
        try:
            logger.info("ParkingController: register_exit")
            return await self.parking_mediator.register_exit(upload_dir, **kwargs)
        except Exception as e:
            logger.error("ParkingController: register_exit failed", exc_info=True)
            raise e

    async def get_status(self, plate_number: str) -> Dict[str, Any]:
        try:
            logger.info("ParkingController: get_status", plate=plate_number)
            return await self.parking_mediator.get_status(plate_number)
        except Exception as e:
            logger.error("ParkingController: get_status failed", exc_info=True)
            raise e

    async def get_all_records(
        self,
        page: int = 1,
        limit: int = 50,
        status_filter: Optional[str] = None,
        date_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            logger.info("ParkingController: get_all_records")
            return await self.parking_mediator.get_all_records(page, limit, status_filter, date_filter)
        except Exception as e:
            logger.error("ParkingController: get_all_records failed", exc_info=True)
            raise e
