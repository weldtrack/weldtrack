from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, String, Text, UniqueConstraint, false, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.core.id import ulid_primary_key


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("email", "date", name="uq_attendance_email_date"),
    )

    id: Mapped[str] = ulid_primary_key(index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    date: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    check_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    check_out_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Existing check_in_at/check_out_at are retained for data compatibility:
    # they now represent Morning In and the final Afternoon Out respectively.
    morning_out_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    afternoon_in_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    hours_worked: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    regular_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    overtime_hours: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Where the check-in/check-out actually happened, captured from the
    # device's GPS at the moment of the request. Kept for audit purposes
    # even though enforcement happens server-side, not on the client.
    check_in_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    check_in_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    check_in_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    check_out_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    check_out_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    check_out_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    morning_out_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    morning_out_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    morning_out_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    afternoon_in_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    afternoon_in_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    afternoon_in_accuracy_m: Mapped[float | None] = mapped_column(Float, nullable=True)

    arrival_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    attendance_status: Mapped[str] = mapped_column(
        String(20), default="Incomplete", server_default="Incomplete", nullable=False
    )
    manually_modified: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
    correction_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    corrected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    corrected_by_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
