from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from app.models.enums import ComplaintGender, ComplaintStatus

class ComplaintBase(BaseModel):
    user_id: UUID
    fullname: str
    gender: ComplaintGender
    complaint_detail: str

class ComplaintCreate(BaseModel):
    fullname: str
    gender: ComplaintGender
    complaint_detail: str

class ComplaintUpdate(BaseModel):
    fullname: Optional[str] = None
    gender: Optional[ComplaintGender] = None
    complaint_detail: Optional[str] = None
    status: Optional[ComplaintStatus] = None

class Complaint(ComplaintBase):
    id: UUID
    tracking_id: str
    status: ComplaintStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
