from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from uuid import UUID
import re

class VoteBase(BaseModel):
    candidate_id: UUID
    voter_name: str
    voter_nic: str
    voter_block: Optional[str] = None
    voter_phone: Optional[str] = None

class VoteCreate(BaseModel):
    candidate_id: UUID
    voter_name: str
    voter_nic: str
    voter_block: Optional[str] = None
    voter_phone: Optional[str] = None

    @field_validator('voter_nic')
    @classmethod
    def validate_cnic(cls, v: str) -> str:
        if not re.match(r'^\d{5}-\d{7}-\d{1}$', v):
            raise ValueError('Invalid CNIC format. Expected: XXXXX-XXXXXXX-X')
        return v
    
    @field_validator('voter_name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v.strip()) < 3:
            raise ValueError('Name must be at least 3 characters')
        return v.strip()

class Vote(VoteBase):
    id: UUID
    voted_at: datetime
    is_verified: bool

    model_config = ConfigDict(from_attributes=True)

class VoteResponse(BaseModel):
    vote_id: UUID
    candidate_name: str
    voted_at: datetime

    model_config = ConfigDict(from_attributes=True)
