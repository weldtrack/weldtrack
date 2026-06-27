import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class CancelledBy(str, enum.Enum):
    admin = "admin"
    customer = "customer"


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), nullable=False, default=BookingStatus.pending
    )

    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    preferred_date: Mapped[str | None] = mapped_column(String(100), nullable=True)
    schedule_date: Mapped[str | None] = mapped_column(String(100), nullable=True)

    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    material_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_price: Mapped[float | None] = mapped_column(Float, nullable=True)

    cancel_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    cancelled_by: Mapped[CancelledBy | None] = mapped_column(
        Enum(CancelledBy), nullable=True
    )

    before_images: Mapped[list | None] = mapped_column(
        JSON, nullable=True, default=list
    )
    after_images: Mapped[list | None] = mapped_column(JSON, nullable=True, default=list)

    # Customer location fields (copied to tasks when creating staff tasks)
    country: Mapped[str] = mapped_column(String(8), default="PH", nullable=False)
    region: Mapped[str] = mapped_column(
        String(64), default="Bicol Region (Region V)", nullable=False
    )
    province: Mapped[str] = mapped_column(String(100), nullable=True)
    municipality: Mapped[str] = mapped_column(String(100), nullable=True)
    barangay: Mapped[str] = mapped_column(String(100), nullable=True)
    house: Mapped[str] = mapped_column(String(150), nullable=True)

    materials: Mapped[list["RecordMaterial"]] = relationship(
        "RecordMaterial",
        back_populates="booking",
        cascade="all, delete-orphan",
    )


class RecordMaterial(Base):
    __tablename__ = "booking_materials"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False
    )
    item_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_temp: Mapped[int | None] = mapped_column(Integer, nullable=True, default=0)

    booking: Mapped["Booking"] = relationship("Booking", back_populates="materials")
