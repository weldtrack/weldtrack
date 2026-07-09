from datetime import datetime

from pydantic import BaseModel, Field


class AttendanceSiteIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    radius_meters: float = Field(ge=20, le=5000)


class AttendanceSiteResponse(BaseModel):
    lat: float
    lng: float
    radius_meters: float
    updated_at: datetime

    class Config:
        from_attributes = True