from typing import Optional, Dict, Any, List
from uuid import UUID

from fastapi import HTTPException, status

from app.schemas.candidate_schema import CandidateCreate, CandidateUpdate, Candidate, CandidateResult
from app.di.container import container
import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class CandidateService:
    @inject
    def __init__(
        self,
        candidate_repository = Provide["candidate_repository"],
        vote_repository = Provide["vote_repository"],
        election_repository = Provide["election_repository"],
        prometheus = Provide["prometheus"],
    ):
        self.candidate_repository = candidate_repository
        self.vote_repository = vote_repository
        self.election_repository = election_repository
        self.prometheus = prometheus
    
    async def get_candidates(self) -> Dict[str, Any]:
        try:
            logger.info("CandidateService: Getting candidates...")
            
            # Get active election
            election = await self.election_repository.findActiveElection()
            
            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active election found"
                )
            
            # Get candidates for this election
            candidates = await self.candidate_repository.findByElectionId(election.id)
            
            # Convert to schemas
            candidate_schemas = [Candidate.model_validate(candidate) for candidate in candidates]
            
            logger.info(f"CandidateService: Got candidates successfully. Total: {len(candidate_schemas)}")
            
            # Record business event
            self.prometheus.record_business_event("candidates_list", "success")
            
            return {
                "success": True,
                "data": candidate_schemas
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("CandidateService: Failed to get candidates.", exc_info=True)
            raise e

    async def get_results(self) -> Dict[str, Any]:
        try:
            logger.info("CandidateService: Getting election results...")
            
            # Get active election
            election = await self.election_repository.findActiveElection()
            
            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active election found"
                )
            
            # Get candidates for this election
            candidates = await self.candidate_repository.findByElectionId(election.id)
            
            # Get total votes
            total_votes = await self.vote_repository.countTotalVotes()
            
            # Calculate votes and percentage for each candidate
            candidate_results = []
            for idx, candidate in enumerate(candidates):
                vote_count = await self.vote_repository.countVotesByCandidateId(candidate.id)
                percentage = 0
                if total_votes > 0:
                    percentage = int((vote_count / total_votes) * 100)
                
                candidate_results.append(CandidateResult(
                    id=candidate.id,
                    name=candidate.name,
                    party=candidate.party,
                    emoji=candidate.emoji,
                    votes=vote_count,
                    percentage=percentage,
                    rank=idx + 1  # Simple ranking by order
                ))
            
            # Sort by votes descending
            candidate_results.sort(key=lambda x: x.votes, reverse=True)
            
            # Update ranks after sorting
            for idx, result in enumerate(candidate_results):
                result.rank = idx + 1
            
            logger.info("CandidateService: Got election results successfully.")
            
            # Record business event
            self.prometheus.record_business_event("election_results", "success")
            
            return {
                "success": True,
                "data": {
                    "total_votes": total_votes,
                    "candidates": candidate_results
                }
            }
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error("CandidateService: Failed to get election results.", exc_info=True)
            raise e
