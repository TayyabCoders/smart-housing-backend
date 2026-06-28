from pydantic import BaseModel, EmailStr
from app.schemas.user_schema import User

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user: User

class TokenData(BaseModel):
    username: str | None = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None

class LogoutRequest(BaseModel):
    refresh_token: str | None = None

class RequestPasswordResetRequest(BaseModel):
    email: EmailStr

class RequestPasswordResetResponse(BaseModel):
    message: str
    reset_token: str | None = None  # Only for development/testing

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ResetPasswordResponse(BaseModel):
    message: str
