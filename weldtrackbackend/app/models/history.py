import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.core.id import ULID_LENGTH, ulid_foreign_key, ulid_primary_key
from app.models.booking import Booking


class BookingHistoryAction(str, enum.Enum):
    created = "created"
    confirmed = "confirmed"
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"
    updated = "updated"


class ProjectHistoryAction(str, enum.Enum):
    created = "created"
    started = "started"
    updated = "updated"
    note_added = "note_added"
    completed = "completed"
    cancelled = "cancelled"


class BookingHistory(Base):
    __tablename__ = "booking_history"

    id: Mapped[str] = ulid_primary_key(index=True)
    booking_id: Mapped[str] = ulid_foreign_key(
        "bookings.id",
        ondelete="CASCADE",
        nullable=False,
        index=True,
    )
    action: Mapped[BookingHistoryAction] = mapped_column(
        Enum(BookingHistoryAction), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status_from: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status_to: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    booking: Mapped["Booking"] = relationship("Booking")


class ProjectHistory(Base):
    __tablename__ = "project_history"

    id: Mapped[str] = ulid_primary_key(index=True)
    booking_id: Mapped[str | None] = ulid_foreign_key(
        "bookings.id",
        ondelete="SET NULL",
        nullable=True,
        index=True,
    )
    task_id: Mapped[str | None] = mapped_column(String(ULID_LENGTH), nullable=True, index=True)
    action: Mapped[ProjectHistoryAction] = mapped_column(
        Enum(ProjectHistoryAction), nullable=False
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    booking: Mapped["Booking | None"] = relationship("Booking")
