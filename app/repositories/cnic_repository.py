from typing import Any, Dict, Optional

from sqlalchemy import select
import structlog
from dependency_injector.wiring import inject, Provide

from app.models.cnic_record_model import CnicRecord
from app.repositories.base_repository import BaseRepository

logger = structlog.get_logger(__name__)


class CnicRepository(BaseRepository):
    @inject
    def __init__(
        self,
        database=Provide["database"],
        cache=Provide["cache"],
    ):
        super().__init__(CnicRecord, database, cache)

    async def find_by_cnic_number(self, cnic_number: str) -> Optional[CnicRecord]:
        try:
            async with self.database.get_session("read") as session:
                stmt = select(CnicRecord).where(CnicRecord.cnic_number == cnic_number)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error("CnicRepository: find_by_cnic_number failed", exc_info=True)
            raise e

    async def upsert(self, cnic_number: str, fields: Dict[str, Any]) -> CnicRecord:
        """Insert a new CNIC record or update known fields on an existing one."""
        try:
            async with self.database.get_session("write") as session:
                stmt = select(CnicRecord).where(CnicRecord.cnic_number == cnic_number)
                result = await session.execute(stmt)
                record = result.scalar_one_or_none()

                if record is None:
                    record = CnicRecord(cnic_number=cnic_number, **{
                        k: v for k, v in fields.items() if v is not None
                    })
                    session.add(record)
                else:
                    for key, value in fields.items():
                        if value is not None:
                            setattr(record, key, value)
                    session.add(record)

                await session.commit()
                await session.refresh(record)
                return record
        except Exception as e:
            logger.error("CnicRepository: upsert failed", exc_info=True)
            raise e
