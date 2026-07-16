from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

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

    async def list_votes(self, filters: dict = None, offset: int = 0, limit: int = 10) -> Dict[str, Any]:
        try:
            logger.info("VoteService: Listing votes...")

            result = await self.vote_repository.findAndCountAll(filters, offset, limit)

            vote_schemas = [Vote.model_validate(vote) for vote in result['rows']]
            result['rows'] = vote_schemas

            logger.info(f"VoteService: Listed votes successfully. Total: {result['total']}")

            return result

        except Exception as e:
            logger.error("VoteService: Failed to list votes.", exc_info=True)
            raise e

    async def submit_vote(self, vote_data: VoteCreate) -> Dict[str, Any]:
        try:
            logger.info("VoteService: Submitting vote...")

            # Check if an active election exists
            election = await self.election_repository.findActiveElection()

            if not election or not election.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "NO_ACTIVE_ELECTION",
                        "message": "No active election found."
                    }
                )

            # Enforce voting window: only allowed on the election date
            today = datetime.now(timezone.utc).date()
            election_date = election.election_date.date()

            if today < election_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "ELECTION_NOT_STARTED",
                        "message": f"Voting has not started yet. Election date is {election_date.strftime('%B %d, %Y')}."
                    }
                )

            if today > election_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "ELECTION_ENDED",
                        "message": "Voting period for this election has ended."
                    }
                )

            # Check if this CNIC has already voted in THIS election
            existing_vote = await self.vote_repository.findByVoterNicAndElectionId(
                vote_data.voter_nic, election.id
            )

            if existing_vote:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "ALREADY_VOTED",
                        "message": "This CNIC has already voted in this election. Each voter can only vote once per election."
                    }
                )

            # Check candidate exists and belongs to this election
            candidate = await self.candidate_repository.findById(vote_data.candidate_id)

            if not candidate:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Candidate not found"
                )

            if str(candidate.election_id) != str(election.id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Candidate does not belong to the active election"
                )

            # Create vote (include election_id)
            vote_dict = vote_data.model_dump()
            vote_dict["election_id"] = election.id
            try:
                vote = await self.vote_repository.create(vote_dict)
            except IntegrityError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "ALREADY_VOTED",
                        "message": "This CNIC has already voted in this election. Each voter can only vote once per election."
                    }
                )

            # Create activity log
            voter_name_short = vote_data.voter_name[:3] + "***" if len(vote_data.voter_name) > 3 else vote_data.voter_name
            activity_text = f"{voter_name_short} ne {candidate.name} ko vote diya"
            await self.activity_log_repository.create({"text": activity_text})

            vote_response = VoteResponse(
                vote_id=vote.id,
                candidate_name=candidate.name,
                voted_at=vote.voted_at
            )

            logger.info(f"VoteService: Vote submitted successfully for candidate: {candidate.name}")

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
