from typing import List, Optional

import structlog
from dependency_injector.wiring import inject, Provide
from sqlalchemy import select

from app.models.camera import Camera
from app.models.enums import CameraType
from app.repositories.base_repository import BaseRepository

logger = structlog.get_logger(__name__)


class CameraRepository(BaseRepository):
    @inject
    def __init__(
        self,
        database=Provide["database"],
        cache=Provide["cache"],
    ):
        super().__init__(Camera, database, cache)

    async def find_by_type(self, camera_type: CameraType, active_only: bool = True) -> List[Camera]:
        try:
            async with self.database.get_session("read") as session:
                stmt = select(Camera).where(Camera.type == camera_type)
                if active_only:
                    stmt = stmt.where(Camera.is_active.is_(True))
                stmt = stmt.order_by(Camera.created_at.asc())
                result = await session.execute(stmt)
                return list(result.scalars().all())
        except Exception as e:
            logger.error("CameraRepository: find_by_type failed", exc_info=True)
            raise e

    async def find_first_by_type(self, camera_type: CameraType, active_only: bool = True) -> Optional[Camera]:
        cameras = await self.find_by_type(camera_type, active_only)
        return cameras[0] if cameras else None
