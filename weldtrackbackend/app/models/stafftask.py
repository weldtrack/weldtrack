import enum
from datetime import date, datetime

from sqlalchemy import (
    String,
    Text,
    Date,
    DateTime,
    Enum,
    Integer,
    func,
    Float
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.core.id import ULID_LENGTH, ulid_foreign_key, ulid_primary_key


class TaskStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in-progress"
    done = "done"


class MovementType(str, enum.Enum):
    stock_out = "stock_out"


class StaffTask(Base):
    __tablename__ = "staff_tasks"

    id: Mapped[str] = ulid_primary_key()

    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    booking_id: Mapped[str | None] = mapped_column(
        String(ULID_LENGTH), nullable=True, index=True
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    due_date: Mapped[date] = mapped_column(Date, nullable=False)

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"),
        default=TaskStatus.pending,
        nullable=False,
    )

    country: Mapped[str] = mapped_column(String(8), default="PH", nullable=False)
    region: Mapped[str] = mapped_column(
        String(64), default="Bicol Region (Region V)", nullable=False
    )
    province: Mapped[str] = mapped_column(String(100), nullable=False)
    municipality: Mapped[str] = mapped_column(String(100), nullable=False)
    barangay: Mapped[str] = mapped_column(String(100), nullable=False)
    house: Mapped[str] = mapped_column(String(150), nullable=False)

    assignees = relationship(
        "StaffTaskAssignee",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    material_usages = relationship(
        "TaskMaterialUsage",
        back_populates="task",
        cascade="all, delete-orphan",
    )


class StaffTaskAssignee(Base):
    __tablename__ = "staff_task_assignees"

    task_id: Mapped[str] = ulid_foreign_key(
        "staff_tasks.id",
        ondelete="CASCADE",
        primary_key=True,
    )

    staff_id: Mapped[str] = ulid_foreign_key(
        "users.id",
        ondelete="CASCADE",
        primary_key=True,
    )

    task = relationship("StaffTask", back_populates="assignees")
    staff = relationship(
        "User", back_populates="assigned_tasks", foreign_keys=[staff_id]
    )


class TaskMaterialUsage(Base):
    __tablename__ = "task_material_usages"

    id: Mapped[str] = ulid_primary_key()

    task_id: Mapped[str] = ulid_foreign_key(
        "staff_tasks.id",
        ondelete="CASCADE",
        nullable=False,
    )

    booking_id: Mapped[str | None] = mapped_column(
        String(ULID_LENGTH), nullable=True
    )

    submitted_by_staff_id: Mapped[str | None] = ulid_foreign_key(
        "users.id",
        ondelete="SET NULL",
        nullable=True,
    )

    movement_type: Mapped[MovementType] = mapped_column(
        Enum(MovementType, name="movement_type"),
        default=MovementType.stock_out,
        nullable=False,
    )

    before_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    labor_hours: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    task = relationship("StaffTask", back_populates="material_usages")
    submitted_by_staff = relationship(
        "User",
        back_populates="material_submissions",
        foreign_keys=[submitted_by_staff_id],
    )

    lines = relationship(
        "TaskMaterialUsageLine",
        back_populates="usage",
        cascade="all, delete-orphan",
    )


class TaskMaterialUsageLine(Base):
    __tablename__ = "task_material_usage_lines"

    id: Mapped[str] = ulid_primary_key()

    usage_id: Mapped[str] = ulid_foreign_key(
        "task_material_usages.id",
        ondelete="CASCADE",
        nullable=False,
    )

    item_id: Mapped[str] = mapped_column(String(ULID_LENGTH), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    usage = relationship("TaskMaterialUsage", back_populates="lines")
