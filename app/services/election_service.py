from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status

from app.schemas.election_schema import ElectionCreate, ElectionUpdate, Election, ElectionStatusResponse, ElectionListItem
from app.di.container import container
from app.models.election import Election as ElectionModel
import structlog
from dependency_injector.wiring import inject, Provide

logger = structlog.get_logger(__name__)


class ElectionService:
    @inject
    def __init__(
        self,
        election_repository = Provide["election_repository"],
        vote_repository = Provide["vote_repository"],
        candidate_service = Provide["candidate_service"],
        candidate_repository = Provide["candidate_repository"],
        prometheus = Provide["prometheus"],
    ):
        self.election_repository = election_repository
        self.vote_repository = vote_repository
        self.candidate_service = candidate_service
        self.candidate_repository = candidate_repository
        self.prometheus = prometheus

    # ─── PUBLIC ──────────────────────────────────────────────────────────────

    async def get_election_status(self) -> Dict[str, Any]:
        try:
            logger.info("ElectionService: Getting election status...")

            election = await self.election_repository.findActiveElection()

            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active election found"
                )

            total_votes_cast = await self.vote_repository.countVotesByElectionId(election.id)

            participation_rate = 0.0
            if election.total_eligible_voters > 0:
                participation_rate = (total_votes_cast / election.total_eligible_voters) * 100

            candidates_resp = await self.candidate_service.get_candidates()
            total_candidates = len(candidates_resp.get("data", []))

            leading = None
            top_candidate = None

            if total_candidates > 0 and total_votes_cast > 0:
                results = await self.candidate_service.get_results()
                candidates_data = results.get("data", {}).get("candidates", [])

                if candidates_data:
                    leading_candidate = next((c for c in candidates_data if c.rank == 1), None)
                    if leading_candidate:
                        leading = leading_candidate.name
                        top_candidate = leading_candidate.percentage

            status_response = ElectionStatusResponse(
                id=election.id,
                title=election.title,
                society_name=election.society_name,
                society_location=election.society_location,
                election_date=election.election_date,
                is_active=election.is_active,
                total_eligible_voters=election.total_eligible_voters,
                total_votes_cast=total_votes_cast,
                participation_rate=round(participation_rate, 2),
                total_candidates=total_candidates,
                leading=leading,
                top_candidate=top_candidate
            )

            logger.info("ElectionService: Got election status successfully.")

            self.prometheus.record_business_event("election_status", "success")

            return {
                "success": True,
                "data": status_response.model_dump()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("ElectionService: Failed to get election status.", exc_info=True)
            raise e

    async def get_election_rules(self) -> Dict[str, Any]:
        try:
            rules = [
                {
                    "icon": "🪪",
                    "title": "CNIC Lazim Hai",
                    "description": "Har voter ko apna valid Pakistani CNIC number dena hoga. Ek CNIC se sirf ek baar vote diya ja sakta hai."
                },
                {
                    "icon": "👤",
                    "title": "Naam Zaroori Hai",
                    "description": "Voter ka poora naam dena lazim hai. Yeh record mein save hoga aur audit ke liye use hoga."
                },
                {
                    "icon": "🏘️",
                    "title": "Society Member",
                    "description": "Sirf Green Valley Society ke registered residents vote de sakte hain. Bahar ke log eligible nahi hain."
                },
                {
                    "icon": "🔒",
                    "title": "Sirf Ek Vote",
                    "description": "Ek voter sirf ek candidate ko vote de sakta hai. Dobara vote dene ki koshish system rokta hai."
                },
                {
                    "icon": "📊",
                    "title": "Shuafaf Nataij",
                    "description": "Live Results tab mein har candidate ke votes real time mein dekhe ja sakte hain. Koi cheez chupayi nahi jati."
                },
                {
                    "icon": "🏆",
                    "title": "Jeet ka Faisla",
                    "description": "Sab se zyada votes hasil karne wala candidate Green Valley Society Committee ka Chairman bane ga."
                }
            ]

            return {
                "success": True,
                "data": {
                    "title": "Election Guidelines",
                    "rules": rules
                }
            }

        except Exception as e:
            logger.error("ElectionService: Failed to get election rules.", exc_info=True)
            raise e

    async def get_election_committee(self) -> Dict[str, Any]:
        try:
            members = [
                {"role": "Presiding Officer", "name": "Rao Tariq Mehmood", "icon": "🧑‍⚖️"},
                {"role": "Secretary", "name": "Mrs. Sana Javed", "icon": "📋"},
                {"role": "Observer", "name": "Haji Abdul Rehman", "icon": "🔍"},
                {"role": "System Admin", "name": "Usman Raza", "icon": "💻"}
            ]

            return {
                "success": True,
                "data": {
                    "title": "Election Committee Members",
                    "members": members
                }
            }

        except Exception as e:
            logger.error("ElectionService: Failed to get election committee.", exc_info=True)
            raise e

    # ─── ADMIN CRUD ───────────────────────────────────────────────────────────

    async def create_election(self, data: ElectionCreate) -> Dict[str, Any]:
        try:
            logger.info("ElectionService: Creating election...")

            # Deactivate any existing active elections so there is always exactly one
            await self.election_repository.deactivateAllExcept()

            election_dict = data.model_dump()
            election_dict["is_active"] = True

            election = await self.election_repository.create(election_dict)

            logger.info(f"ElectionService: Created election {election.id}")

            self.prometheus.record_business_event("election_created", "success")

            return {
                "success": True,
                "message": "Election created successfully",
                "data": Election.model_validate(election).model_dump()
            }

        except Exception as e:
            logger.error("ElectionService: Failed to create election.", exc_info=True)
            raise e

    async def list_elections(self) -> Dict[str, Any]:
        try:
            logger.info("ElectionService: Listing all elections...")

            elections = await self.election_repository.findAll()

            today = datetime.now(timezone.utc).date()
            election_list = []

            for election in elections:
                candidates = await self.candidate_repository.findByElectionId(election.id)
                total_candidates = len(candidates)
                total_votes = await self.vote_repository.countVotesByElectionId(election.id)

                election_date = election.election_date.date()
                if not election.is_active:
                    election_status = "closed"
                elif election_date > today:
                    election_status = "upcoming"
                elif election_date == today:
                    election_status = "active"
                else:
                    election_status = "closed"

                election_list.append(ElectionListItem(
                    id=election.id,
                    title=election.title,
                    society_name=election.society_name,
                    society_location=election.society_location,
                    election_date=election.election_date,
                    is_active=election.is_active,
                    total_eligible_voters=election.total_eligible_voters,
                    total_candidates=total_candidates,
                    total_votes=total_votes,
                    status=election_status,
                    created_at=election.created_at
                ))

            # Sort: active first, then upcoming, then closed
            order = {"active": 0, "upcoming": 1, "closed": 2}
            election_list.sort(key=lambda e: order.get(e.status, 3))

            logger.info(f"ElectionService: Listed {len(election_list)} elections.")

            return {
                "success": True,
                "data": [e.model_dump() for e in election_list]
            }

        except Exception as e:
            logger.error("ElectionService: Failed to list elections.", exc_info=True)
            raise e

    async def update_election(self, election_id: UUID, data: ElectionUpdate) -> Dict[str, Any]:
        try:
            logger.info(f"ElectionService: Updating election {election_id}...")

            election = await self.election_repository.findById(election_id)

            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Election not found"
                )

            update_dict = {k: v for k, v in data.model_dump().items() if v is not None}

            updated = await self.election_repository.update(election_id, update_dict)

            logger.info(f"ElectionService: Updated election {election_id}")

            return {
                "success": True,
                "message": "Election updated successfully",
                "data": Election.model_validate(updated).model_dump()
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("ElectionService: Failed to update election.", exc_info=True)
            raise e

    async def delete_election(self, election_id: UUID) -> Dict[str, Any]:
        try:
            logger.info(f"ElectionService: Deleting election {election_id}...")

            election = await self.election_repository.findById(election_id)

            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Election not found"
                )

            # Block deletion if any votes have been cast
            total_votes = await self.vote_repository.countVotesByElectionId(election_id)
            if total_votes > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot delete election with {total_votes} recorded vote(s). Deactivate it instead."
                )

            # Delete candidates first (FK constraint)
            candidates = await self.candidate_repository.findByElectionId(election_id)
            for candidate in candidates:
                await self.candidate_repository.delete(candidate.id)

            await self.election_repository.delete(election_id)

            logger.info(f"ElectionService: Deleted election {election_id}")

            return {
                "success": True,
                "message": "Election deleted successfully"
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("ElectionService: Failed to delete election.", exc_info=True)
            raise e
