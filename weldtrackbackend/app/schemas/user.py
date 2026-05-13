from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr


class SignupRequest(UserBase):
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    is_banned: bool = False
    is_online: bool = False
    last_active: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(AuthToken):
    user: UserRead