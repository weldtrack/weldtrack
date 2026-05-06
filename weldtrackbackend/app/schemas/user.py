from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    name: str | None = None


class SignupRequest(UserBase):
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(AuthToken):
    user: UserRead