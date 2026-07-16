from typing import Optional
from uuid import UUID

from sqlalchemy import select

from app.repositories.base_repository import BaseRepository
from app.models.vote import Vote
from app.models.candidate import Candidate

from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger
from typing import Any

logger = get_logger(__name__)

class VoteRepository(BaseRepository[Vote]):
    @inject
    def __init__(self, database = Provide["database"], cache: Optional[Any] = Provide["cache"]):
        super().__init__(Vote, database, cache)

    async def findByVoterNicAndElectionId(self, voter_nic: str, election_id: UUID) -> Optional[Vote]:
        try:
            logger.info("VoteRepository: Finding vote by voter_nic and election_id...")

            vote = await self.findOne(filters={"voter_nic": voter_nic, "election_id": election_id})

            logger.info("VoteRepository: Found vote by voter_nic and election_id.")

            return vote

        except Exception as e:
            logger.error("VoteRepository: Failed to find vote by voter_nic and election_id.", exc_info=True)
            raise e

    async def findByCandidateId(self, candidate_id: UUID) -> list[Vote]:
        try:
            logger.info("VoteRepository: Finding votes by candidate_id...")

            votes = await self.findAll(filters={"candidate_id": candidate_id})

            logger.info("VoteRepository: Found votes by candidate_id.")

            return votes

        except Exception as e:
            logger.error("VoteRepository: Failed to find votes by candidate_id.", exc_info=True)
            raise e

    async def countVotesByCandidateId(self, candidate_id: UUID) -> int:
        try:
            logger.info("VoteRepository: Counting votes by candidate_id...")

            count = await self.count(filters={"candidate_id": candidate_id})

            logger.info("VoteRepository: Counted votes by candidate_id.")

            return count

        except Exception as e:
            logger.error("VoteRepository: Failed to count votes by candidate_id.", exc_info=True)
            raise e

    async def countVotesByElectionId(self, election_id: UUID) -> int:
        try:
            logger.info("VoteRepository: Counting votes by election_id...")

            count = await self.count(filters={"election_id": election_id})

            logger.info("VoteRepository: Counted votes by election_id.")

            return count

        except Exception as e:
            logger.error("VoteRepository: Failed to count votes by election_id.", exc_info=True)
            raise e

    async def countTotalVotes(self) -> int:
        try:
            logger.info("VoteRepository: Counting total votes...")

            count = await self.count()

            logger.info("VoteRepository: Counted total votes.")

            return count

        except Exception as e:
            logger.error("VoteRepository: Failed to count total votes.", exc_info=True)
            raise e
