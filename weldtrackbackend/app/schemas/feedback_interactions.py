from pydantic import BaseModel, EmailStr
from datetime import datetime


class FeedbackCommentBase(BaseModel):
    comment: str


class FeedbackCommentCreate(FeedbackCommentBase):
    pass


class FeedbackCommentResponse(FeedbackCommentBase):
    id: int
    feedback_id: int
    user_email: EmailStr
    date: datetime

    class Config:
        from_attributes = True


class FeedbackLikeResponse(BaseModel):
    id: int
    feedback_id: int
    user_email: EmailStr

    class Config:
        from_attributes = True
