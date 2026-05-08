from pydantic import BaseModel
from datetime import datetime


class AttendanceBase(BaseModel):
    email: str


class AttendanceCheckIn(AttendanceBase):
    pass


class AttendanceCheckOut(BaseModel):
    email: str


class AttendanceResponse(BaseModel):
    id: int
    email: str
    date: str
    check_in_at: datetime
    check_out_at: datetime | None = None
    hours_worked: float
    regular_hours: float
    overtime_hours: float

    class Config:
        from_attributes = True