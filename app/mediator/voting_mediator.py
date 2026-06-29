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

    async def get_candidates(self):
        try:
            logger.info("VotingMediator: Getting candidates...")
            
            result = await self.candidate_service.get_candidates()
            
            logger.info("VotingMediator: Got candidates successfully.")
            
            return result
        
        except Exception as e:
            logger.error("VotingMediator: Failed to get candidates.", exc_info=True)
            raise e

    async def submit_vote(self, vote_data):
        try:
            logger.info("VotingMediator: Submitting vote...")
            
            result = await self.vote_service.submit_vote(vote_data)
            
            logger.info("VotingMediator: Vote submitted successfully.")
            
            return result
        
        except Exception as e:
            logger.error("VotingMediator: Failed to submit vote.", exc_info=True)
            raise e

    async def get_results(self):
        try:
            logger.info("VotingMediator: Getting results...")
            
            result = await self.candidate_service.get_results()
            
            logger.info("VotingMediator: Got results successfully.")
            
            return result
        
        except Exception as e:
            logger.error("VotingMediator: Failed to get results.", exc_info=True)
            raise e

    async def get_activity_log(self, limit: int = 15):
        try:
            logger.info("VotingMediator: Getting activity log...")
            
            result = await self.activity_log_service.get_activity_log(limit)
            
            logger.info("VotingMediator: Got activity log successfully.")
            
            return result
        
        except Exception as e:
            logger.error("VotingMediator: Failed to get activity log.", exc_info=True)
            raise e

    async def get_election_status(self):
        try:
            logger.info("VotingMediator: Getting election status...")
            
            result = await self.election_service.get_election_status()
            
            logger.info("VotingMediator: Got election status successfully.")
            
            return result
        
        except Exception as e:
            logger.error("VotingMediator: Failed to get election status.", exc_info=True)
            raise e

    async def get_election_rules(self):
        try:
            logger.info("VotingMediator: Getting election rules...")
            
            result = await self.election_service.get_election_rules()
            
            logger.info("VotingMediator: Got election rules successfully.")
            
            return result
        
        except Exception as e:
            logger.error("VotingMediator: Failed to get election rules.", exc_info=True)
            raise e

    async def get_election_committee(self):
        try:
            logger.info("VotingMediator: Getting election committee...")
            
            result = await self.election_service.get_election_committee()
            
            logger.info("VotingMediator: Got election committee successfully.")
            
            return result
        
        except Exception as e:
            logger.error("VotingMediator: Failed to get election committee.", exc_info=True)
            raise e
