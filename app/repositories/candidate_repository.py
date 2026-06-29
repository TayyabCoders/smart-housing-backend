from typing import Optional
from app.repositories.base_repository import BaseRepository
from app.models.candidate import Candidate

from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from typing import Any
from uuid import UUID

logger = get_logger(__name__)

class CandidateRepository(BaseRepository[Candidate]):
    @inject
    def __init__(self, database = Provide["database"], cache : Optional[Any] = Provide["cache"]):
        super().__init__(Candidate, database, cache)

    async def findByElectionId(self, election_id: UUID) -> list[Candidate]:
        try:
            logger.info("CandidateRepository: Finding candidates by election_id...")
            
            candidates = await self.findAll(filters={"election_id": election_id})
            
            logger.info("CandidateRepository: Found candidates by election_id.")
            
            return candidates
        
        except Exception as e:
            logger.error("CandidateRepository: Failed to find candidates by election_id.", exc_info=True)
            raise e
