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
    full_name: Optional[str] = None
    province: Optional[str] = None
    municipality: Optional[str] = None
    barangay: Optional[str] = None
    house: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: str
    full_name: Optional[str] = None
    role: UserRole
    created_at: Optional[datetime] = None
    is_banned: bool = False
    is_online: bool = False
    last_active: Optional[datetime] = None
    profile_image: Optional[str] = None
    mobile_phone: Optional[str] = None

    @field_validator("id", mode="before")
    @classmethod
    def normalize_id(cls, value):
        return str(value) if value is not None else ""

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return str(value).strip().lower() if value else ""

    @field_validator("role", mode="before")
    @classmethod
    def normalize_role(cls, value):
        if isinstance(value, str):
            val = value.strip().lower()
            try:
                return UserRole(val)
            except ValueError:
                return UserRole.customer
        if hasattr(value, "value"):
            val = str(value.value).strip().lower()
            try:
                return UserRole(val)
            except ValueError:
                return UserRole.customer
        return value

    @field_validator("is_banned", "is_online", mode="before")
    @classmethod
    def normalize_bool(cls, value):
        if value is None:
            return False
        return bool(value)


class UserUpdate(BaseModel):
    fullname: Optional[str] = None
    full_name: Optional[str] = None
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
