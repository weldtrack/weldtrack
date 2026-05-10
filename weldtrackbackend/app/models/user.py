import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Boolean, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    staff = "staff"
    customer = "customer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        default=UserRole.customer,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    is_banned: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    is_online: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    last_active: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    logged_out_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="When the user last logged out - used to invalidate old tokens"
    )
    
    email_verification = relationship(
        "EmailVerification",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    assigned_tasks = relationship(
        "StaffTaskAssignee",
        back_populates="staff",
        foreign_keys="StaffTaskAssignee.staff_id",
    )
    material_submissions = relationship(
        "TaskMaterialUsage",
        back_populates="submitted_by_staff",
        foreign_keys="TaskMaterialUsage.submitted_by_staff_id",
    )