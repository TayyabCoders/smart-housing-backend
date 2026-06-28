from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime
from uuid import UUID
from app.models.user_model import Gender, Role

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str
    phone_number: Optional[str] = None
    age: Optional[int] = None
    role: Optional[Role] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone_number: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[Gender] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[Role] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class User(UserBase):
    id: UUID
    role: str
    is_active: bool
    phone_number: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    zip_code: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class PasswordResetToken(BaseModel):
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class RefreshToken(BaseModel):
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime
    is_revoked: bool = False
    
    model_config = ConfigDict(from_attributes=True)
