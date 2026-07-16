from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import UploadFile

logger = structlog.get_logger(__name__)


class FaceMediator:
    @inject
    def __init__(
        self,
        face_service=Provide["face_service"],
    ):
        self.face_service = face_service

    async def detect_and_match(self, file: UploadFile, camera_id: UUID) -> Dict[str, Any]:
        try:
            logger.info("FaceMediator: detect_and_match")
            return await self.face_service.detect_and_match(file, camera_id)
        except Exception as e:
            logger.error("FaceMediator: detect_and_match failed", exc_info=True)
            raise e

    async def enroll(
        self,
        file: UploadFile,
        person_id: Optional[UUID],
        name: Optional[str],
        role: Optional[str],
        flat_no: Optional[str],
        phone: Optional[str],
    ) -> Dict[str, Any]:
        try:
            logger.info("FaceMediator: enroll")
            return await self.face_service.enroll(file, person_id, name, role, flat_no, phone)
        except Exception as e:
            logger.error("FaceMediator: enroll failed", exc_info=True)
            raise e

    async def list_detections(
        self,
        camera_id: Optional[UUID],
        status: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
        search: Optional[str],
        offset: int,
        limit: int,
    ) -> Dict[str, Any]:
        try:
            logger.info("FaceMediator: list_detections")
            return await self.face_service.list_detections(
                camera_id, status, date_from, date_to, search, offset, limit
            )
        except Exception as e:
            logger.error("FaceMediator: list_detections failed", exc_info=True)
            raise e

    async def apply_action(self, detection_id: UUID, action: str, acted_by: UUID) -> Dict[str, Any]:
        try:
            logger.info("FaceMediator: apply_action")
            return await self.face_service.apply_action(detection_id, action, acted_by)
        except Exception as e:
            logger.error("FaceMediator: apply_action failed", exc_info=True)
            raise e
