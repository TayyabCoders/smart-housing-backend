"""
Upload Schema
"""
from pydantic import BaseModel


class UploadResponse(BaseModel):
    success: bool
    message: str
    data: dict
