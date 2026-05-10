from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, func, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class EmailVerificationCode(Base):
    """Temporary storage for email verification codes during signup"""
    __tablename__ = "email_verification_codes"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(6), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EmailVerification(Base):
    """Email verification status and code for existing users"""
    __tablename__ = "email_verifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    verification_code: Mapped[str | None] = mapped_column(String(6), nullable=True)
    code_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship(
        "User",
        back_populates="email_verification",
        uselist=False
    )

