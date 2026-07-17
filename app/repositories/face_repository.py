from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

import structlog
from dependency_injector.wiring import inject, Provide
from sqlalchemy import and_, func, select
from sqlalchemy.orm import selectinload

from app.models.camera import Camera
from app.models.enums import DetectionStatus
from app.models.face_detection import FaceDetection
from app.models.face_embedding import FaceEmbedding
from app.models.person import Person
from app.repositories.base_repository import BaseRepository

logger = structlog.get_logger(__name__)


class FaceRepository(BaseRepository):
    @inject
    def __init__(
        self,
        database=Provide["database"],
        cache=Provide["cache"],
    ):
        super().__init__(FaceDetection, database, cache)

    async def find_closest_person(
        self, embedding: List[float], similarity_threshold: float = 0.6
    ) -> Optional[Tuple[Person, float]]:
        """Return (person, similarity) for the closest enrolled face, or None if below threshold."""
        try:
            async with self.database.get_session("read") as session:
                distance_col = FaceEmbedding.vector.cosine_distance(embedding).label("distance")
                stmt = (
                    select(Person, distance_col)
                    .join(FaceEmbedding, FaceEmbedding.person_id == Person.id)
                    .where(Person.is_active.is_(True))
                    .order_by(distance_col.asc())
                    .limit(1)
                )
                result = await session.execute(stmt)
                row = result.first()
                if not row:
                    return None

                person, distance = row
                similarity = 1 - float(distance)
                if similarity < similarity_threshold:
                    return None
                return person, similarity
        except Exception as e:
            logger.error("FaceRepository: find_closest_person failed", exc_info=True)
            raise e

    async def create_embedding(
        self, person_id: UUID, vector: List[float], image_url: Optional[str]
    ) -> FaceEmbedding:
        try:
            async with self.database.get_session("write") as session:
                embedding = FaceEmbedding(person_id=person_id, vector=vector, image_url=image_url)
                session.add(embedding)
                await session.commit()
                await session.refresh(embedding)
                return embedding
        except Exception as e:
            logger.error("FaceRepository: create_embedding failed", exc_info=True)
            raise e

    async def create_person(self, data: Dict[str, Any]) -> Person:
        try:
            async with self.database.get_session("write") as session:
                person = Person(**data)
                session.add(person)
                await session.commit()
                await session.refresh(person)
                return person
        except Exception as e:
            logger.error("FaceRepository: create_person failed", exc_info=True)
            raise e

    async def get_person(self, person_id: UUID) -> Optional[Person]:
        try:
            async with self.database.get_session("read") as session:
                stmt = select(Person).where(Person.id == person_id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error("FaceRepository: get_person failed", exc_info=True)
            raise e

    async def list_detections(
        self,
        camera_id: Optional[UUID] = None,
        status: Optional[DetectionStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Dict[str, Any]:
        try:
            async with self.database.get_session("read") as session:
                conditions = []
                if camera_id:
                    conditions.append(FaceDetection.camera_id == camera_id)
                if status:
                    conditions.append(FaceDetection.status == status)
                if date_from:
                    conditions.append(FaceDetection.detected_at >= date_from)
                if date_to:
                    conditions.append(FaceDetection.detected_at <= date_to)

                base_stmt = select(FaceDetection).outerjoin(
                    Person, FaceDetection.matched_person_id == Person.id
                )
                if search:
                    conditions.append(Person.name.ilike(f"%{search}%"))
                if conditions:
                    base_stmt = base_stmt.where(and_(*conditions))

                count_stmt = select(func.count()).select_from(base_stmt.subquery())
                total = (await session.execute(count_stmt)).scalar()

                stmt = (
                    base_stmt.options(
                        selectinload(FaceDetection.matched_person),
                        selectinload(FaceDetection.camera),
                    )
                    .order_by(FaceDetection.detected_at.desc())
                    .offset(offset)
                    .limit(limit)
                )
                result = await session.execute(stmt)
                items = list(result.scalars().unique().all())

                return {"items": items, "total": total, "offset": offset, "limit": limit}
        except Exception as e:
            logger.error("FaceRepository: list_detections failed", exc_info=True)
            raise e

    async def get_stats(self, since: Optional[datetime] = None) -> Dict[str, int]:
        try:
            async with self.database.get_session("read") as session:
                stmt = select(FaceDetection.status, func.count()).group_by(FaceDetection.status)
                if since:
                    stmt = stmt.where(FaceDetection.detected_at >= since)
                result = await session.execute(stmt)
                counts = {row[0].value: row[1] for row in result.all()}

                return {
                    "total": sum(counts.values()),
                    "residents": counts.get(DetectionStatus.RESIDENT.value, 0),
                    "staff": counts.get(DetectionStatus.STAFF.value, 0),
                    "visitors": counts.get(DetectionStatus.VISITOR.value, 0),
                    "unknown": counts.get(DetectionStatus.UNKNOWN.value, 0),
                    "blacklist": counts.get(DetectionStatus.BLACKLIST.value, 0),
                }
        except Exception as e:
            logger.error("FaceRepository: get_stats failed", exc_info=True)
            raise e

    async def update_action(
        self, detection_id: UUID, action, acted_by: UUID
    ) -> Optional[FaceDetection]:
        return await self.update(detection_id, {"action_taken": action, "acted_by": acted_by})
