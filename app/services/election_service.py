from typing import Optional, Dict, Any
from uuid import UUID

from fastapi import HTTPException, status

from app.schemas.election_schema import ElectionCreate, ElectionUpdate, Election, ElectionStatusResponse
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
        prometheus = Provide["prometheus"],
    ):
        self.election_repository = election_repository
        self.vote_repository = vote_repository
        self.candidate_service = candidate_service
        self.prometheus = prometheus
    
    async def get_election_status(self) -> ElectionStatusResponse:
        try:
            logger.info("ElectionService: Getting election status...")
            
            election = await self.election_repository.findActiveElection()
            
            if not election:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No active election found"
                )
            
            # Get total votes cast
            total_votes_cast = await self.vote_repository.countTotalVotes()
            
            # Calculate participation rate
            participation_rate = 0.0
            if election.total_eligible_voters > 0:
                participation_rate = (total_votes_cast / election.total_eligible_voters) * 100
            
            # Get candidates for this election
            candidates = await self.candidate_service.get_candidates()
            total_candidates = len(candidates.get("data", []))
            
            # Get leading candidate info
            leading = None
            top_candidate = None
            
            if total_candidates > 0 and total_votes_cast > 0:
                results = await self.candidate_service.get_results()
                candidates_data = results.get("data", {}).get("candidates", [])
                
                if candidates_data:
                    # Find the candidate with highest votes (rank 1)
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
            
            # Record business event
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
            logger.info("ElectionService: Getting election rules...")
            
            # Static rules as per requirements
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
            
            logger.info("ElectionService: Got election rules successfully.")
            
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
            logger.info("ElectionService: Getting election committee...")
            
            # Static committee members as per requirements
            members = [
                {
                    "role": "Presiding Officer",
                    "name": "Rao Tariq Mehmood",
                    "icon": "🧑‍⚖️"
                },
                {
                    "role": "Secretary",
                    "name": "Mrs. Sana Javed",
                    "icon": "📋"
                },
                {
                    "role": "Observer",
                    "name": "Haji Abdul Rehman",
                    "icon": "🔍"
                },
                {
                    "role": "System Admin",
                    "name": "Usman Raza",
                    "icon": "💻"
                }
            ]
            
            logger.info("ElectionService: Got election committee successfully.")
            
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
