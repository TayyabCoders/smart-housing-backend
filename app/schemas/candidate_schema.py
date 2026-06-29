from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class CandidateBase(BaseModel):
    election_id: UUID
    name: str
    role: str
    party: str
    p_class: str
    emoji: str

class CandidateCreate(BaseModel):
    election_id: UUID
    name: str
    role: str
    party: str
    p_class: str
    emoji: str

class CandidateUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    party: Optional[str] = None
    p_class: Optional[str] = None
    emoji: Optional[str] = None

class Candidate(CandidateBase):
    id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CandidateResult(BaseModel):
    id: UUID
    name: str
    party: str
    emoji: str
    votes: int
    percentage: int
    rank: int

    model_config = ConfigDict(from_attributes=True)
