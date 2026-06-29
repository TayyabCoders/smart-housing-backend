from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status

from app.schemas.vote_schema import VoteCreate, Vote, VoteResponse
from app.schemas.activity_log_schema import ActivityLogCreate
from app.di.container import container
import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class VoteService:
    @inject
    def __init__(
        self,
        vote_repository = Provide["vote_repository"],
        candidate_repository = Provide["candidate_repository"],
        activity_log_repository = Provide["activity_log_repository"],
        election_repository = Provide["election_repository"],
        prometheus = Provide["prometheus"],
    ):
        self.vote_repository = vote_repository
        self.candidate_repository = candidate_repository
        self.activity_log_repository = activity_log_repository
        self.election_repository = election_repository
        self.prometheus = prometheus
    
    async def submit_vote(self, vote_data: VoteCreate) -> Dict[str, Any]:
        try:
            logger.info("VoteService: Submitting vote...")
            
            # Check if election is active
            election = await self.election_repository.findActiveElection()
            
            if not election or not election.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No active election found"
                )
            
            # Check if CNIC has already voted
            existing_vote = await self.vote_repository.findByVoterNic(vote_data.voter_nic)
            
            if existing_vote:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "ALREADY_VOTED",
                        "message": "This CNIC has already been used to vote. Each voter can only vote once."
                    }
                )
            
            # Check if candidate exists
            candidate = await self.candidate_repository.findById(vote_data.candidate_id)
            
            if not candidate:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Candidate not found"
                )
            
            # Create vote
            vote_dict = vote_data.model_dump()
            vote = await self.vote_repository.create(vote_dict)
            
            # Create activity log
            voter_name_short = vote_data.voter_name[:3] + "***" if len(vote_data.voter_name) > 3 else vote_data.voter_name
            activity_text = f"{voter_name_short} ne {candidate.name} ko vote diya"
            await self.activity_log_repository.create({"text": activity_text})
            
            # Prepare response
            vote_response = VoteResponse(
                vote_id=vote.id,
                candidate_name=candidate.name,
                voted_at=vote.voted_at
            )
            
            logger.info(f"VoteService: Vote submitted successfully for candidate: {candidate.name}")
            
            # Record business event
            self.prometheus.record_business_event("vote_submission", "success")
            
            return {
                "success": True,
                "message": "Vote successfully recorded",
                "data": vote_response
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("VoteService: Failed to submit vote.", exc_info=True)
            raise e
