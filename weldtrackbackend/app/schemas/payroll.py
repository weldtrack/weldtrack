from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.payroll import PayslipStatus


class PayslipCreate(BaseModel):
    staff_id: str
    period_start: date
    period_end: date
    hourly_rate: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    overtime_rate: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    allowances: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    bonuses: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    deductions: Decimal = Field(default=Decimal("0"), ge=0, max_digits=12, decimal_places=2)
    notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_period(self):
        if self.period_end < self.period_start:
            raise ValueError("period_end must be on or after period_start")
        return self


class PayslipStatusUpdate(BaseModel):
    status: PayslipStatus


class PayslipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    staff_id: str
    staff_email: str
    period_start: date
    period_end: date
    regular_hours: Decimal
    overtime_hours: Decimal
    hourly_rate: Decimal
    overtime_rate: Decimal
    regular_pay: Decimal
    overtime_pay: Decimal
    allowances: Decimal
    bonuses: Decimal
    deductions: Decimal
    gross_pay: Decimal
    net_pay: Decimal
    notes: str | None
    status: PayslipStatus
    created_by_id: str | None
    created_at: datetime
    updated_at: datetime
