from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.schemas.feedback_interactions import (
    FeedbackCommentResponse,
    FeedbackLikeResponse,
)


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
    id: str
    date: datetime
    profile_image: str | None = None
    comments: list[FeedbackCommentResponse] = []
    likes: list[FeedbackLikeResponse] = []

    class Config:
        from_attributes = True
