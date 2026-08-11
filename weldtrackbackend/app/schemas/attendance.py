from pydantic import BaseModel, Field
from datetime import datetime


class AttendanceLocation(BaseModel):
    lat: float | None = Field(default=None, ge=-90, le=90)
    lng: float | None = Field(default=None, ge=-180, le=180)
    accuracy: float | None = Field(default=None, ge=0)


class AttendanceCorrection(BaseModel):
    morning_in_at: datetime | None = None
    morning_out_at: datetime | None = None
    afternoon_in_at: datetime | None = None
    afternoon_out_at: datetime | None = None
    reason: str = Field(min_length=3, max_length=1000)


class AttendanceResponse(BaseModel):
    id: str
    email: str
    date: str
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None
    morning_in_at: datetime | None = None
    morning_out_at: datetime | None = None
    afternoon_in_at: datetime | None = None
    afternoon_out_at: datetime | None = None
    morning_hours: float = 0
    afternoon_hours: float = 0
    total_hours_worked: float = 0
    hours_worked: float
    regular_hours: float
    overtime_hours: float
    arrival_status: str | None = None
    attendance_status: str
    next_action: str | None = None
    next_action_available: bool = False
    next_action_available_at: datetime | None = None
    next_action_message: str = ""
    attendance_date: str
    timezone: str
    manually_modified: bool = False
    correction_note: str | None = None
    corrected_at: datetime | None = None
    corrected_by_email: str | None = None

    class Config:
        from_attributes = True
