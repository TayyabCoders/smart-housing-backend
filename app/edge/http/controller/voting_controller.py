from uuid import UUID

from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger

logger = get_logger(__name__)

class VotingController:
    @inject
    def __init__(self, voting_mediator = Provide["voting_mediator"]):
        self.voting_mediator = voting_mediator

    # ─── PUBLIC ──────────────────────────────────────────────────────────────

    async def get_candidates(self):
        try:
            return await self.voting_mediator.get_candidates()
        except Exception as e:
            logger.error("VotingController: Failed to get candidates.", exc_info=True)
            raise e

    async def submit_vote(self, vote_data):
        try:
            return await self.voting_mediator.submit_vote(vote_data)
        except Exception as e:
            logger.error("VotingController: Failed to submit vote.", exc_info=True)
            raise e

    async def get_results(self):
        try:
            return await self.voting_mediator.get_results()
        except Exception as e:
            logger.error("VotingController: Failed to get results.", exc_info=True)
            raise e

    async def get_activity_log(self, limit: int = 15):
        try:
            return await self.voting_mediator.get_activity_log(limit)
        except Exception as e:
            logger.error("VotingController: Failed to get activity log.", exc_info=True)
            raise e

    async def get_election_status(self):
        try:
            return await self.voting_mediator.get_election_status()
        except Exception as e:
            logger.error("VotingController: Failed to get election status.", exc_info=True)
            raise e

    async def get_election_rules(self):
        try:
            return await self.voting_mediator.get_election_rules()
        except Exception as e:
            logger.error("VotingController: Failed to get election rules.", exc_info=True)
            raise e

    async def get_election_committee(self):
        try:
            return await self.voting_mediator.get_election_committee()
        except Exception as e:
            logger.error("VotingController: Failed to get election committee.", exc_info=True)
            raise e

    # ─── ADMIN ───────────────────────────────────────────────────────────────

    async def create_election(self, data):
        try:
            return await self.voting_mediator.create_election(data)
        except Exception as e:
            logger.error("VotingController: Failed to create election.", exc_info=True)
            raise e

    async def list_elections(self):
        try:
            return await self.voting_mediator.list_elections()
        except Exception as e:
            logger.error("VotingController: Failed to list elections.", exc_info=True)
            raise e

    async def update_election(self, election_id: UUID, data):
        try:
            return await self.voting_mediator.update_election(election_id, data)
        except Exception as e:
            logger.error("VotingController: Failed to update election.", exc_info=True)
            raise e

    async def delete_election(self, election_id: UUID):
        try:
            return await self.voting_mediator.delete_election(election_id)
        except Exception as e:
            logger.error("VotingController: Failed to delete election.", exc_info=True)
            raise e

    async def create_candidate(self, data):
        try:
            return await self.voting_mediator.create_candidate(data)
        except Exception as e:
            logger.error("VotingController: Failed to create candidate.", exc_info=True)
            raise e

    async def update_candidate(self, candidate_id: UUID, data):
        try:
            return await self.voting_mediator.update_candidate(candidate_id, data)
        except Exception as e:
            logger.error("VotingController: Failed to update candidate.", exc_info=True)
            raise e

    async def delete_candidate(self, candidate_id: UUID):
        try:
            return await self.voting_mediator.delete_candidate(candidate_id)
        except Exception as e:
            logger.error("VotingController: Failed to delete candidate.", exc_info=True)
            raise e

    async def get_candidates_by_election(self, election_id: UUID):
        try:
            return await self.voting_mediator.get_candidates_by_election(election_id)
        except Exception as e:
            logger.error("VotingController: Failed to get candidates by election.", exc_info=True)
            raise e
