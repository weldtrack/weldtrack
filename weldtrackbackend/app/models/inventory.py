import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.core.id import ULID_LENGTH, ulid_foreign_key, ulid_primary_key
from app.models.booking import Booking


class MovementType(str, enum.Enum):
    stock_in = "stock_in"
    stock_out = "stock_out"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[str] = ulid_primary_key(index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    supplier: Mapped[str | None] = mapped_column(String(255), nullable=True)
    low_stock_threshold: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date_added: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    movements: Mapped[list["StockMovement"]] = relationship(
        "StockMovement",
        back_populates="item",
        cascade="all, delete-orphan",
    )


class StockMovement(Base):
    __tablename__ = "stock_movements"

    id: Mapped[str] = ulid_primary_key(index=True)
    item_id: Mapped[str] = ulid_foreign_key(
        "inventory_items.id",
        ondelete="CASCADE",
        nullable=False,
        index=True,
    )
    item_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[MovementType] = mapped_column(Enum(MovementType), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    booking_id: Mapped[str | None] = ulid_foreign_key(
        "bookings.id",
        ondelete="SET NULL",
        nullable=True,
        index=True,
    )
    task_id: Mapped[str | None] = mapped_column(String(ULID_LENGTH), nullable=True, index=True)

    item: Mapped["InventoryItem"] = relationship(
        "InventoryItem", back_populates="movements"
    )
    booking: Mapped["Booking | None"] = relationship("Booking")
