from pydantic import BaseModel
from datetime import datetime


class AttendanceBase(BaseModel):
    user_id: int


class AttendanceCheckIn(AttendanceBase):
    pass


class AttendanceCheckOut(BaseModel):
    user_id: int


class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    date: str
    check_in_at: datetime
    check_out_at: datetime | None = None
    hours_worked: float
    regular_hours: float
    overtime_hours: float

    class Config:
        from_attributes = True