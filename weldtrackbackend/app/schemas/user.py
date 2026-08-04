from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class SignupRequest(UserBase):
    password: str = Field(min_length=8)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: datetime
    is_banned: bool = False
    is_online: bool = False
    last_active: Optional[datetime] = None
    profile_image: Optional[str] = None
    mobile_phone: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    mobile_phone: Optional[str] = Field(None, max_length=20)
    profile_image: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)


class CurrentUserResponse(UserRead):
    pass


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(AuthToken):
    user: UserRead
