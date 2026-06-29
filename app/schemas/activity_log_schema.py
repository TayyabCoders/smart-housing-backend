from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID

class ActivityLogBase(BaseModel):
    text: str

class ActivityLogCreate(BaseModel):
    text: str

class ActivityLog(ActivityLogBase):
    id: UUID
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)

class ActivityLogResponse(BaseModel):
    text: str
    time: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
