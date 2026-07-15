from datetime import datetime, date
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DetectResponse(BaseModel):
    detected: bool
    plate_number: Optional[str] = None
    confidence: Optional[float] = None
    snapshot_url: Optional[str] = None
    message: str
    # Vehicle registry lookup result
    resident_status: Optional[str] = None  # resident | visitor | staff | blacklist | unknown
    owner_name: Optional[str] = None
    flat_number: Optional[str] = None
    vehicle_type: Optional[str] = None


class EntryResponse(BaseModel):
    plate_number: str
    cnic_number: Optional[str] = None
    entry_image_url: Optional[str] = None
    entry_time: datetime
    status: Literal["IN"]
    message: str


class ExitResponse(BaseModel):
    plate_number: str
    entry_time: datetime
    cnic_number: str
    exit_image_url: Optional[str] = None
    exit_time: datetime
    duration_minutes: int
    fee: int
    message: str


class StatusResponse(BaseModel):
    plate_number: str
    status: Literal["IN", "OUT"]
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    elapsed_minutes: Optional[int] = None
    current_fee: Optional[int] = None
    grace_period_remaining_minutes: Optional[int] = None
    total_fee_paid: Optional[int] = None


class ParkingRecord(BaseModel):
    plate_number: str
    status: Literal["IN", "OUT"]
    entry_time: datetime
    exit_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    fee: Optional[int] = None
    entry_image_url: Optional[str] = None
    exit_image_url: Optional[str] = None
    elapsed_minutes: Optional[int] = None
    current_fee: Optional[int] = None


class AllRecordsResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[ParkingRecord]
