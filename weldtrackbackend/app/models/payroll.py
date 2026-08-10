import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.id import ulid_foreign_key, ulid_primary_key
from app.db import Base


class PayslipStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    paid = "paid"


class Payslip(Base):
    __tablename__ = "payslips"
    __table_args__ = (
        UniqueConstraint(
            "staff_id", "period_start", "period_end", name="uq_payslip_staff_period"
        ),
    )

    id: Mapped[str] = ulid_primary_key(index=True)
    staff_id: Mapped[str] = ulid_foreign_key(
        "users.id", ondelete="CASCADE", nullable=False, index=True
    )
    staff_email: Mapped[str] = mapped_column(String(255), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    regular_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    overtime_hours: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    overtime_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    regular_pay: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    overtime_pay: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    allowances: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    bonuses: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    deductions: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gross_pay: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    net_pay: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    status: Mapped[PayslipStatus] = mapped_column(
        Enum(PayslipStatus, name="payslip_status"),
        default=PayslipStatus.draft,
        nullable=False,
    )
    created_by_id: Mapped[str | None] = ulid_foreign_key(
        "users.id", ondelete="SET NULL", nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    staff = relationship("User", foreign_keys=[staff_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
