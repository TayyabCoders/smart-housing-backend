"""
Voting system endpoints
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from app.schemas.vote_schema import VoteCreate
from app.schemas.election_schema import ElectionCreate, ElectionUpdate
from app.schemas.candidate_schema import CandidateCreate, CandidateUpdate
from app.edge.http.controller.voting_controller import VotingController
from app.middlewares.auth_middleware import require_admin
from app.di.container import container
from dependency_injector.wiring import inject, Provide

router = APIRouter()


# ─── PUBLIC ENDPOINTS ────────────────────────────────────────────────────────

@router.get("/candidates", response_model=dict)
@inject
async def get_candidates(
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Get all candidates for the active election"""
    return await voting_controller.get_candidates()


@router.post("/vote", response_model=dict)
@inject
async def submit_vote(
    vote_data: VoteCreate,
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Submit a vote for a candidate (only allowed on election date)"""
    return await voting_controller.submit_vote(vote_data)


@router.get("/results", response_model=dict)
@inject
async def get_results(
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Get live election results"""
    return await voting_controller.get_results()


@router.get("/activity-log", response_model=dict)
@inject
async def get_activity_log(
    limit: int = Query(15, ge=1, le=50),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Get recent voting activity"""
    return await voting_controller.get_activity_log(limit)


@router.get("/election/status", response_model=dict)
@inject
async def get_election_status(
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Get current election status"""
    return await voting_controller.get_election_status()


@router.get("/election/rules", response_model=dict)
@inject
async def get_election_rules(
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Get election rules and guidelines"""
    return await voting_controller.get_election_rules()


@router.get("/election/committee", response_model=dict)
@inject
async def get_election_committee(
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Get election committee members"""
    return await voting_controller.get_election_committee()


# ─── ADMIN ENDPOINTS ─────────────────────────────────────────────────────────

@router.get("/admin/elections", response_model=dict)
@inject
async def list_elections(
    _ = Depends(require_admin),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Admin: List all elections with status"""
    return await voting_controller.list_elections()


@router.post("/admin/elections", response_model=dict)
@inject
async def create_election(
    data: ElectionCreate,
    _ = Depends(require_admin),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Admin: Create a new election"""
    return await voting_controller.create_election(data)


@router.put("/admin/elections/{election_id}", response_model=dict)
@inject
async def update_election(
    election_id: UUID,
    data: ElectionUpdate,
    _ = Depends(require_admin),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Admin: Update election details or activate/deactivate it"""
    return await voting_controller.update_election(election_id, data)


@router.delete("/admin/elections/{election_id}", response_model=dict)
@inject
async def delete_election(
    election_id: UUID,
    _ = Depends(require_admin),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Admin: Delete an election (only if no votes cast)"""
    return await voting_controller.delete_election(election_id)


@router.get("/admin/elections/{election_id}/candidates", response_model=dict)
@inject
async def get_candidates_by_election(
    election_id: UUID,
    _ = Depends(require_admin),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Admin: Get candidates for any election by ID"""
    return await voting_controller.get_candidates_by_election(election_id)


@router.post("/admin/candidates", response_model=dict)
@inject
async def create_candidate(
    data: CandidateCreate,
    _ = Depends(require_admin),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Admin: Add a candidate to an election"""
    return await voting_controller.create_candidate(data)


@router.put("/admin/candidates/{candidate_id}", response_model=dict)
@inject
async def update_candidate(
    candidate_id: UUID,
    data: CandidateUpdate,
    _ = Depends(require_admin),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Admin: Update a candidate"""
    return await voting_controller.update_candidate(candidate_id, data)


@router.delete("/admin/candidates/{candidate_id}", response_model=dict)
@inject
async def delete_candidate(
    candidate_id: UUID,
    _ = Depends(require_admin),
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Admin: Delete a candidate (only if no votes cast for them)"""
    return await voting_controller.delete_candidate(candidate_id)
