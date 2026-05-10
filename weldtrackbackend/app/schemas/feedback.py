from pydantic import BaseModel, EmailStr
from datetime import datetime


class FeedbackBase(BaseModel):
    email: EmailStr
    project_type: str
    rating: float
    comment: str


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(BaseModel):
    email: EmailStr | None = None
    project_type: str | None = None
    rating: float | None = None
    comment: str | None = None


class FeedbackResponse(FeedbackBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True