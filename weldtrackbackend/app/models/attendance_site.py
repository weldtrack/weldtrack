from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class AttendanceSite(Base):
    """The single fixed location staff must be within to check in/out.

    Only ever expected to hold one row. Reads use the most recently updated
    row so re-saving never requires deleting the old one first.
    """

    __tablename__ = "attendance_site"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lng: Mapped[float] = mapped_column(Float, nullable=False)
    radius_meters: Mapped[float] = mapped_column(Float, nullable=False, default=150.0)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )