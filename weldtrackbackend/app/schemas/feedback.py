from pydantic import BaseModel, EmailStr
from datetime import datetime


# Base fields (shared)
class FeedbackBase(BaseModel):
    email: EmailStr
    project_type: str
    rating: float
    comment: str


# CREATE (POST /feedbacks)
class FeedbackCreate(FeedbackBase):
    pass


# UPDATE (PUT /feedbacks/{id})
class FeedbackUpdate(BaseModel):
    email: EmailStr | None = None
    project_type: str | None = None
    rating: float | None = None
    comment: str | None = None


# RESPONSE (what frontend receives)
class FeedbackResponse(FeedbackBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True