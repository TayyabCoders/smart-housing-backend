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

    # ─── PUBLIC ──────────────────────────────────────────────────────────────

    async def get_candidates(self) -> Dict[str, Any]:
        try:
            logger.info("CandidateService: Getting candidates...")

            election = await self.election_repository.findActiveElection()

            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active election found"
                )

            candidates = await self.candidate_repository.findByElectionId(election.id)
            candidate_schemas = [Candidate.model_validate(c) for c in candidates]

            logger.info(f"CandidateService: Got {len(candidate_schemas)} candidates.")

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

            election = await self.election_repository.findActiveElection()

            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active election found"
                )

            candidates = await self.candidate_repository.findByElectionId(election.id)
            total_votes = await self.vote_repository.countVotesByElectionId(election.id)

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
                    rank=idx + 1
                ))

            candidate_results.sort(key=lambda x: x.votes, reverse=True)

            for idx, result in enumerate(candidate_results):
                result.rank = idx + 1

            logger.info("CandidateService: Got election results successfully.")

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

    # ─── ADMIN CRUD ───────────────────────────────────────────────────────────

    async def get_candidates_by_election(self, election_id: UUID) -> Dict[str, Any]:
        try:
            candidates = await self.candidate_repository.findByElectionId(election_id)
            candidate_schemas = [Candidate.model_validate(c) for c in candidates]
            return {"success": True, "data": candidate_schemas}
        except Exception as e:
            logger.error("CandidateService: Failed to get candidates by election.", exc_info=True)
            raise e

    async def create_candidate(self, data: CandidateCreate) -> Dict[str, Any]:
        try:
            logger.info("CandidateService: Creating candidate...")

            election = await self.election_repository.findById(data.election_id)
            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Election not found"
                )

            candidate = await self.candidate_repository.create(data.model_dump())

            logger.info(f"CandidateService: Created candidate {candidate.id}")

            self.prometheus.record_business_event("candidate_created", "success")

            return {
                "success": True,
                "message": "Candidate added successfully",
                "data": Candidate.model_validate(candidate).model_dump()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("CandidateService: Failed to create candidate.", exc_info=True)
            raise e

    async def update_candidate(self, candidate_id: UUID, data: CandidateUpdate) -> Dict[str, Any]:
        try:
            logger.info(f"CandidateService: Updating candidate {candidate_id}...")

            candidate = await self.candidate_repository.findById(candidate_id)
            if not candidate:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Candidate not found"
                )

            update_dict = {k: v for k, v in data.model_dump().items() if v is not None}
            updated = await self.candidate_repository.update(candidate_id, update_dict)

            return {
                "success": True,
                "message": "Candidate updated successfully",
                "data": Candidate.model_validate(updated).model_dump()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("CandidateService: Failed to update candidate.", exc_info=True)
            raise e

    async def delete_candidate(self, candidate_id: UUID) -> Dict[str, Any]:
        try:
            logger.info(f"CandidateService: Deleting candidate {candidate_id}...")

            candidate = await self.candidate_repository.findById(candidate_id)
            if not candidate:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Candidate not found"
                )

            votes = await self.vote_repository.countVotesByCandidateId(candidate_id)
            if votes > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete candidate with {votes} recorded vote(s)."
                )

            await self.candidate_repository.delete(candidate_id)

            return {
                "success": True,
                "message": "Candidate deleted successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("CandidateService: Failed to delete candidate.", exc_info=True)
            raise e
