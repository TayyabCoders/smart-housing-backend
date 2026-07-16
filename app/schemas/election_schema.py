from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class ElectionBase(BaseModel):
    title: str
    society_name: str
    society_location: str
    election_date: datetime
    is_active: bool
    total_eligible_voters: int

class ElectionCreate(BaseModel):
    title: str
    society_name: str
    society_location: str
    election_date: datetime
    total_eligible_voters: int

class ElectionUpdate(BaseModel):
    title: Optional[str] = None
    society_name: Optional[str] = None
    society_location: Optional[str] = None
    election_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    total_eligible_voters: Optional[int] = None

class Election(ElectionBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ElectionListItem(BaseModel):
    id: UUID
    title: str
    society_name: str
    society_location: str
    election_date: datetime
    is_active: bool
    total_eligible_voters: int
    total_candidates: int
    total_votes: int
    status: str  # "upcoming" | "active" | "closed"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ElectionStatusResponse(BaseModel):
    id: UUID
    title: str
    society_name: str
    society_location: str
    election_date: datetime
    is_active: bool
    total_eligible_voters: int
    total_votes_cast: int
    participation_rate: float
    total_candidates: int
    leading: Optional[str] = None
    top_candidate: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
