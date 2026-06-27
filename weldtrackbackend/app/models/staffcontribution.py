from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class StaffContributionSnapshot(Base):
    __tablename__ = "staff_contribution_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    booking_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)
    task_title: Mapped[str] = mapped_column(String(200), nullable=False)
    contributor_ids: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    contributor_emails: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
