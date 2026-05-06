from datetime import datetime
from sqlalchemy.orm import Session

from app.models.attendance import AttendanceRecord
from app.models.user import User, UserRole


WORK_DAY_HOURS = 8


def check_in(db: Session, user: User):
    if user.role != UserRole.staff:
        raise ValueError("Only staff can check in")

    today = datetime.utcnow().date().isoformat()

    record = AttendanceRecord(
        user_id=user.id,
        date=today,
        check_in_at=datetime.utcnow(),
        hours_worked=0,
        regular_hours=0,
        overtime_hours=0
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def check_out(db: Session, user: User):
    today = datetime.utcnow().date().isoformat()

    record = (
        db.query(AttendanceRecord)
        .filter(
            AttendanceRecord.user_id == user.id,
            AttendanceRecord.date == today
        )
        .first()
    )

    if not record:
        raise ValueError("No check-in found")

    record.check_out_at = datetime.utcnow()

    hours = (record.check_out_at - record.check_in_at).total_seconds() / 3600

    record.hours_worked = round(hours, 2)
    record.regular_hours = min(hours, WORK_DAY_HOURS)
    record.overtime_hours = max(0, hours - WORK_DAY_HOURS)

    db.commit()
    db.refresh(record)
    return record