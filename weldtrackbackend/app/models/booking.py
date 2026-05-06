import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class BookingStatus(str, enum.Enum):
    pending   = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class CancelledBy(str, enum.Enum):
    admin    = "admin"
    customer = "customer"


class Booking(Base):
    __tablename__ = "bookings"

    id:             Mapped[int]           = mapped_column(Integer, primary_key=True, index=True)
    project_type:   Mapped[str]           = mapped_column(String(255), nullable=False)
    status:         Mapped[BookingStatus] = mapped_column(Enum(BookingStatus), nullable=False, default=BookingStatus.pending)

    # Customer info
    customer_name:  Mapped[str | None]   = mapped_column(String(255), nullable=True)
    email:          Mapped[str | None]   = mapped_column(String(255), nullable=True)
    phone:          Mapped[str | None]   = mapped_column(String(50),  nullable=True)
    description:    Mapped[str | None]   = mapped_column(Text,        nullable=True)

    # Dates
    created_date:   Mapped[datetime]     = mapped_column(DateTime(timezone=True), server_default=func.now())
    preferred_date: Mapped[str | None]   = mapped_column(String(100), nullable=True)
    schedule_date:  Mapped[str | None]   = mapped_column(String(100), nullable=True)

    # Costs
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    material_cost:  Mapped[float | None] = mapped_column(Float, nullable=True)
    total_price:    Mapped[float | None] = mapped_column(Float, nullable=True)

    # Cancellation
    cancel_reason:  Mapped[str | None]        = mapped_column(Text,               nullable=True)
    cancelled_by:   Mapped[CancelledBy | None] = mapped_column(Enum(CancelledBy), nullable=True)

    # Images
    before_images:  Mapped[list | None]  = mapped_column(JSON, nullable=True, default=list)
    after_images:   Mapped[list | None]  = mapped_column(JSON, nullable=True, default=list)

    # Relationship
    materials: Mapped[list["BookingMaterial"]] = relationship(
        "BookingMaterial",
        back_populates="booking",
        cascade="all, delete-orphan",
    )


class BookingMaterial(Base):
    __tablename__ = "booking_materials"

    id:         Mapped[int]        = mapped_column(Integer, primary_key=True, index=True)
    booking_id: Mapped[int]        = mapped_column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    item_id:    Mapped[str]        = mapped_column(String(100), nullable=False)
    name:       Mapped[str]        = mapped_column(String(255), nullable=False)
    qty:        Mapped[int]        = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float]      = mapped_column(Float,   nullable=False, default=0.0)
    subtotal:   Mapped[float]      = mapped_column(Float,   nullable=False, default=0.0)
    is_temp:    Mapped[int | None] = mapped_column(Integer, nullable=True,  default=0)

    booking: Mapped["Booking"] = relationship("Booking", back_populates="materials")