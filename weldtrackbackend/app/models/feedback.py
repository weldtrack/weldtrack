from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.core.id import ulid_primary_key


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = ulid_primary_key(index=True)

    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    project_type: Mapped[str] = mapped_column(String(255), nullable=False)

    rating: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str] = mapped_column(String(1000), nullable=False)

    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    comments = relationship(
        "FeedbackComment", back_populates="feedback", cascade="all, delete-orphan"
    )
    likes = relationship(
        "FeedbackLike", back_populates="feedback", cascade="all, delete-orphan"
    )
