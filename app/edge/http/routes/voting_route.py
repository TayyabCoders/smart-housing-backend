"""
Voting system endpoints
"""
from fastapi import APIRouter, Depends, Query
from app.schemas.vote_schema import VoteCreate
from app.edge.http.controller.voting_controller import VotingController
from app.di.container import container
from dependency_injector.wiring import inject, Provide

router = APIRouter()


@router.get("/candidates", response_model=dict)
@inject
async def get_candidates(
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Get all candidates for the election"""
    return await voting_controller.get_candidates()


@router.post("/vote", response_model=dict)
@inject
async def submit_vote(
    vote_data: VoteCreate,
    voting_controller: VotingController = Depends(Provide["voting_controller"])
):
    """Submit a vote for a candidate"""
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
