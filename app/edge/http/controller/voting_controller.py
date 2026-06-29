from app.di.container import container
from dependency_injector.wiring import inject, Provide
from structlog import get_logger

logger = get_logger(__name__)

class VotingController:
    @inject
    def __init__(self, voting_mediator = Provide["voting_mediator"]):
        self.voting_mediator = voting_mediator

    async def get_candidates(self):
        try:
            logger.info("VotingController: Getting candidates...")
            
            result = await self.voting_mediator.get_candidates()
            
            logger.info("VotingController: Got candidates successfully.")
            
            return result 

        except Exception as e:
            logger.error("VotingController: Failed to get candidates.", exc_info=True)
            raise e

    async def submit_vote(self, vote_data):
        try:
            logger.info("VotingController: Submitting vote...")
            
            result = await self.voting_mediator.submit_vote(vote_data)
            
            logger.info("VotingController: Vote submitted successfully.")

            return result 

        except Exception as e:
            logger.error("VotingController: Failed to submit vote.", exc_info=True)
            raise e

    async def get_results(self):
        try:
            logger.info("VotingController: Getting results...")
            
            result = await self.voting_mediator.get_results()
            
            logger.info("VotingController: Got results successfully.")

            return result 

        except Exception as e:
            logger.error("VotingController: Failed to get results.", exc_info=True)
            raise e

    async def get_activity_log(self, limit: int = 15):
        try:
            logger.info("VotingController: Getting activity log...")
            
            result = await self.voting_mediator.get_activity_log(limit)
            
            logger.info("VotingController: Got activity log successfully.")

            return result 

        except Exception as e:
            logger.error("VotingController: Failed to get activity log.", exc_info=True)
            raise e

    async def get_election_status(self):
        try:
            logger.info("VotingController: Getting election status...")
            
            result = await self.voting_mediator.get_election_status()
            
            logger.info("VotingController: Got election status successfully.")

            return result 

        except Exception as e:
            logger.error("VotingController: Failed to get election status.", exc_info=True)
            raise e

    async def get_election_rules(self):
        try:
            logger.info("VotingController: Getting election rules...")
            
            result = await self.voting_mediator.get_election_rules()
            
            logger.info("VotingController: Got election rules successfully.")

            return result 

        except Exception as e:
            logger.error("VotingController: Failed to get election rules.", exc_info=True)
            raise e

    async def get_election_committee(self):
        try:
            logger.info("VotingController: Getting election committee...")
            
            result = await self.voting_mediator.get_election_committee()
            
            logger.info("VotingController: Got election committee successfully.")

            return result 

        except Exception as e:
            logger.error("VotingController: Failed to get election committee.", exc_info=True)
            raise e
