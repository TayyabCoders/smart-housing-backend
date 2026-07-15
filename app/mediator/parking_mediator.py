from pathlib import Path
from typing import Any, Dict, Optional

import structlog
from dependency_injector.wiring import inject, Provide


logger = structlog.get_logger(__name__)


class ParkingMediator:
    @inject
    def __init__(
        self,
        parking_service=Provide["parking_service"],
    ):
        self.parking_service = parking_service

    async def register_entry(self, upload_dir: Path, **kwargs) -> Dict[str, Any]:
        try:
            logger.info("ParkingMediator: register_entry")
            return await self.parking_service.register_entry(upload_dir, **kwargs)
        except Exception as e:
            logger.error("ParkingMediator: register_entry failed", exc_info=True)
            raise e

    async def register_exit(self, upload_dir: Path, **kwargs) -> Dict[str, Any]:
        try:
            logger.info("ParkingMediator: register_exit")
            return await self.parking_service.register_exit(upload_dir, **kwargs)
        except Exception as e:
            logger.error("ParkingMediator: register_exit failed", exc_info=True)
            raise e

    async def get_status(self, plate_number: str) -> Dict[str, Any]:
        try:
            logger.info("ParkingMediator: get_status", plate=plate_number)
            return await self.parking_service.get_status(plate_number)
        except Exception as e:
            logger.error("ParkingMediator: get_status failed", exc_info=True)
            raise e

    async def get_all_records(
        self,
        page: int = 1,
        limit: int = 50,
        status_filter: Optional[str] = None,
        date_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        try:
            logger.info("ParkingMediator: get_all_records")
            return await self.parking_service.get_all_records(page, limit, status_filter, date_filter)
        except Exception as e:
            logger.error("ParkingMediator: get_all_records failed", exc_info=True)
            raise e

    async def detect_plate(
        self,
        image_file_bytes: bytes,
        image_file_suffix: str,
        upload_dir: Path,
    ) -> Dict[str, Any]:
        try:
            logger.info("ParkingMediator: detect_plate")
            return await self.parking_service.detect_plate(image_file_bytes, image_file_suffix, upload_dir)
        except Exception as e:
            logger.error("ParkingMediator: detect_plate failed", exc_info=True)
            raise e
