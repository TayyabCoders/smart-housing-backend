from uuid import UUID

from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger

logger = get_logger(__name__)

class VotingMediator:
    @inject
    def __init__(
        self,
        election_service = Provide["election_service"],
        candidate_service = Provide["candidate_service"],
        vote_service = Provide["vote_service"],
        activity_log_service = Provide["activity_log_service"]
    ):
        self.election_service = election_service
        self.candidate_service = candidate_service
        self.vote_service = vote_service
        self.activity_log_service = activity_log_service

    # ─── PUBLIC ──────────────────────────────────────────────────────────────

    async def get_candidates(self):
        try:
            return await self.candidate_service.get_candidates()
        except Exception as e:
            logger.error("VotingMediator: Failed to get candidates.", exc_info=True)
            raise e

    async def submit_vote(self, vote_data):
        try:
            return await self.vote_service.submit_vote(vote_data)
        except Exception as e:
            logger.error("VotingMediator: Failed to submit vote.", exc_info=True)
            raise e

    async def get_results(self):
        try:
            return await self.candidate_service.get_results()
        except Exception as e:
            logger.error("VotingMediator: Failed to get results.", exc_info=True)
            raise e

    async def get_activity_log(self, limit: int = 15):
        try:
            return await self.activity_log_service.get_activity_log(limit)
        except Exception as e:
            logger.error("VotingMediator: Failed to get activity log.", exc_info=True)
            raise e

    async def get_election_status(self):
        try:
            return await self.election_service.get_election_status()
        except Exception as e:
            logger.error("VotingMediator: Failed to get election status.", exc_info=True)
            raise e

    async def get_election_rules(self):
        try:
            return await self.election_service.get_election_rules()
        except Exception as e:
            logger.error("VotingMediator: Failed to get election rules.", exc_info=True)
            raise e

    async def get_election_committee(self):
        try:
            return await self.election_service.get_election_committee()
        except Exception as e:
            logger.error("VotingMediator: Failed to get election committee.", exc_info=True)
            raise e

    # ─── ADMIN ───────────────────────────────────────────────────────────────

    async def create_election(self, data):
        try:
            return await self.election_service.create_election(data)
        except Exception as e:
            logger.error("VotingMediator: Failed to create election.", exc_info=True)
            raise e

    async def list_elections(self):
        try:
            return await self.election_service.list_elections()
        except Exception as e:
            logger.error("VotingMediator: Failed to list elections.", exc_info=True)
            raise e

    async def update_election(self, election_id: UUID, data):
        try:
            return await self.election_service.update_election(election_id, data)
        except Exception as e:
            logger.error("VotingMediator: Failed to update election.", exc_info=True)
            raise e

    async def delete_election(self, election_id: UUID):
        try:
            return await self.election_service.delete_election(election_id)
        except Exception as e:
            logger.error("VotingMediator: Failed to delete election.", exc_info=True)
            raise e

    async def create_candidate(self, data):
        try:
            return await self.candidate_service.create_candidate(data)
        except Exception as e:
            logger.error("VotingMediator: Failed to create candidate.", exc_info=True)
            raise e

    async def update_candidate(self, candidate_id: UUID, data):
        try:
            return await self.candidate_service.update_candidate(candidate_id, data)
        except Exception as e:
            logger.error("VotingMediator: Failed to update candidate.", exc_info=True)
            raise e

    async def delete_candidate(self, candidate_id: UUID):
        try:
            return await self.candidate_service.delete_candidate(candidate_id)
        except Exception as e:
            logger.error("VotingMediator: Failed to delete candidate.", exc_info=True)
            raise e

    async def get_candidates_by_election(self, election_id: UUID):
        try:
            return await self.candidate_service.get_candidates_by_election(election_id)
        except Exception as e:
            logger.error("VotingMediator: Failed to get candidates by election.", exc_info=True)
            raise e
