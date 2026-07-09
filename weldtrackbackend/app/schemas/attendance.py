from pydantic import BaseModel, Field
from datetime import datetime


class AttendanceCheckIn(BaseModel):
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)


class AttendanceCheckOut(BaseModel):
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)


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