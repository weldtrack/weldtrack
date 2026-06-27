from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class FeedbackComment(Base):
    __tablename__ = "feedback_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedbacks.id"), nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False)
    comment: Mapped[str] = mapped_column(String(1000), nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    feedback = relationship("Feedback", back_populates="comments")


class FeedbackLike(Base):
    __tablename__ = "feedback_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedbacks.id"), nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False)

    feedback = relationship("Feedback", back_populates="likes")
