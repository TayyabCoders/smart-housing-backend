from typing import Optional
from sqlalchemy import select, desc, update

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
        """Returns the most recently created active election (safe when multiple exist)."""
        try:
            logger.info("ElectionRepository: Finding active election...")

            async with self.database.get_session("read") as session:
                stmt = (
                    select(Election)
                    .where(Election.is_active == True)
                    .order_by(desc(Election.created_at))
                    .limit(1)
                )
                result = await session.execute(stmt)
                election = result.scalar_one_or_none()

            logger.info("ElectionRepository: Found active election.")
            return election

        except Exception as e:
            logger.error("ElectionRepository: Failed to find active election.", exc_info=True)
            raise e

    async def deactivateAllExcept(self, exclude_id=None) -> None:
        """Set is_active=False on all elections (optionally except one)."""
        try:
            async with self.database.get_session("write") as session:
                stmt = update(Election).where(Election.is_active == True)
                if exclude_id:
                    stmt = stmt.where(Election.id != exclude_id)
                stmt = stmt.values(is_active=False)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            logger.error("ElectionRepository: Failed to deactivate elections.", exc_info=True)
            raise e
