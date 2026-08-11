from datetime import date, datetime, time
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import (
    ATTENDANCE_AFTERNOON_IN_OPEN,
    ATTENDANCE_AFTERNOON_IN_CLOSE,
    ATTENDANCE_LATE_AFTER,
    ATTENDANCE_MORNING_CLOSE,
    ATTENDANCE_MORNING_OPEN,
    ATTENDANCE_MORNING_OUT_OPEN,
    ATTENDANCE_REGULAR_HOURS,
    ATTENDANCE_TIMEZONE,
)
from app.db import get_db
from app.geo import haversine_meters
from app.models.attendance import AttendanceRecord
from app.models.attendance_site import AttendanceSite
from app.models.user import User, UserRole
from app.router.auth import get_current_user
from app.schemas.attendance import (
    AttendanceCorrection,
    AttendanceLocation,
    AttendanceResponse,
)

router = APIRouter(prefix="/attendance", tags=["attendance"])

ATTENDANCE_TZ = ZoneInfo(ATTENDANCE_TIMEZONE)
MAX_ATTENDANCE_ACCURACY_M = 30


def _schedule_time(value: str) -> time:
    try:
        return time.fromisoformat(value)
    except ValueError as exc:
        raise RuntimeError(f"Invalid attendance schedule time: {value}") from exc


MORNING_OPEN = _schedule_time(ATTENDANCE_MORNING_OPEN)
MORNING_CLOSE = _schedule_time(ATTENDANCE_MORNING_CLOSE)
LATE_AFTER = _schedule_time(ATTENDANCE_LATE_AFTER)
MORNING_OUT_OPEN = _schedule_time(ATTENDANCE_MORNING_OUT_OPEN)
AFTERNOON_IN_OPEN = _schedule_time(ATTENDANCE_AFTERNOON_IN_OPEN)
AFTERNOON_IN_CLOSE = _schedule_time(ATTENDANCE_AFTERNOON_IN_CLOSE)

if MORNING_OPEN >= MORNING_CLOSE:
    raise RuntimeError("Morning attendance opening time must be before its closing time")
if AFTERNOON_IN_OPEN >= AFTERNOON_IN_CLOSE:
    raise RuntimeError("Afternoon attendance opening time must be before its closing time")


def _now_manila() -> datetime:
    return datetime.now(ATTENDANCE_TZ)


def _as_manila(value: datetime) -> datetime:
    # SQLite can return timezone-naive values even for timezone=True columns.
    # Existing values were written as UTC; treat naive historical values as UTC.
    if value.tzinfo is None:
        return value.replace(tzinfo=ZoneInfo("UTC")).astimezone(ATTENDANCE_TZ)
    return value.astimezone(ATTENDANCE_TZ)


def _require_attendance_role(user: User) -> None:
    if user.role not in (UserRole.admin, UserRole.staff):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Attendance access is restricted to staff and admins")


def _require_admin(user: User) -> None:
    if user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can perform this action")


def _configured_site(db: Session) -> AttendanceSite:
    site = db.scalar(select(AttendanceSite).order_by(desc(AttendanceSite.updated_at)))
    if not site:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance location is not configured. Ask an admin to configure the attendance geofence.",
        )
    return site


def _enforce_geofence(db: Session, payload: AttendanceLocation) -> None:
    site = _configured_site(db)
    if payload.lat is None or payload.lng is None or payload.accuracy is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Latitude, longitude, and GPS accuracy are required")
    if payload.accuracy > MAX_ATTENDANCE_ACCURACY_M:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"GPS accuracy is insufficient (±{round(payload.accuracy)}m). Move to an open area and try again.",
        )
    distance = haversine_meters(site.lat, site.lng, payload.lat, payload.lng)
    if distance > site.radius_meters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are outside the authorized attendance area ({round(distance)}m away; allowed radius is {round(site.radius_meters)}m).",
        )


def _hours_between(start: datetime | None, end: datetime | None) -> float:
    if not start or not end:
        return 0.0
    return max(0.0, (_as_manila(end) - _as_manila(start)).total_seconds() / 3600)


def _recalculate(record: AttendanceRecord) -> tuple[float, float]:
    # Records completed before the four-event model have only the legacy
    # check_in_at/check_out_at pair. Preserve their stored totals and treat
    # them as completed history instead of incorrectly recalculating zero.
    if record.check_out_at and not record.morning_out_at and not record.afternoon_in_at:
        record.attendance_status = "Completed"
        return 0.0, 0.0
    morning = _hours_between(record.check_in_at, record.morning_out_at)
    afternoon = _hours_between(record.afternoon_in_at, record.check_out_at)
    total = round(morning + afternoon, 2)
    record.hours_worked = total
    record.regular_hours = round(min(total, ATTENDANCE_REGULAR_HOURS), 2)
    record.overtime_hours = round(max(0.0, total - ATTENDANCE_REGULAR_HOURS), 2)
    record.attendance_status = "Completed" if all((record.check_in_at, record.morning_out_at, record.afternoon_in_at, record.check_out_at)) else "Incomplete"
    return round(morning, 2), round(afternoon, 2)


def _next_action(record: AttendanceRecord | None, now: datetime) -> tuple[str | None, bool, str]:
    current_time = now.timetz().replace(tzinfo=None)
    if record and record.check_out_at and not record.morning_out_at and not record.afternoon_in_at:
        return None, False, "Attendance for this legacy record is already completed."
    # A staff member who missed the morning window may still attend the
    # afternoon session. After 8 AM, guide an unstarted day toward the next
    # relevant Time In instead of leaving the UI stuck on Morning Time In.
    if record is None or record.check_in_at is None:
        if record and record.afternoon_in_at:
            if record.check_out_at is None:
                return "afternoon-out", True, "Afternoon time-out is available."
            return None, False, "Attendance for today is already completed."
        if current_time >= MORNING_CLOSE:
            allowed = AFTERNOON_IN_OPEN <= current_time < AFTERNOON_IN_CLOSE
            if current_time < AFTERNOON_IN_OPEN:
                message = f"Morning Time In has closed. Afternoon Time In opens at {AFTERNOON_IN_OPEN.strftime('%-I:%M %p')}."
            elif current_time >= AFTERNOON_IN_CLOSE:
                message = f"Afternoon Time In closed at {AFTERNOON_IN_CLOSE.strftime('%-I:%M %p')}. Ask an admin to correct a missed attendance event."
            else:
                message = f"Afternoon Time In is available until {AFTERNOON_IN_CLOSE.strftime('%-I:%M %p')}."
            return "afternoon-in", allowed, message
        allowed = MORNING_OPEN <= current_time < MORNING_CLOSE
        if current_time < MORNING_OPEN:
            message = f"Morning Time In opens at {MORNING_OPEN.strftime('%-I:%M %p')} and closes at {MORNING_CLOSE.strftime('%-I:%M %p')}."
        elif current_time >= MORNING_CLOSE:
            message = f"Morning Time In closed at {MORNING_CLOSE.strftime('%-I:%M %p')}. Ask an admin to correct a missed attendance event."
        else:
            message = f"Morning Time In is available until {MORNING_CLOSE.strftime('%-I:%M %p')}."
        return "morning-in", allowed, message
    if record.morning_out_at is None:
        allowed = current_time >= MORNING_OUT_OPEN
        message = "Morning time-out is available." if allowed else f"Morning time-out is available at {MORNING_OUT_OPEN.strftime('%-I:%M %p')}."
        return "morning-out", allowed, message
    if record.afternoon_in_at is None:
        allowed = AFTERNOON_IN_OPEN <= current_time < AFTERNOON_IN_CLOSE
        if current_time < AFTERNOON_IN_OPEN:
            message = f"Afternoon Time In opens at {AFTERNOON_IN_OPEN.strftime('%-I:%M %p')} and closes at {AFTERNOON_IN_CLOSE.strftime('%-I:%M %p')}."
        elif current_time >= AFTERNOON_IN_CLOSE:
            message = f"Afternoon Time In closed at {AFTERNOON_IN_CLOSE.strftime('%-I:%M %p')}. Ask an admin to correct a missed attendance event."
        else:
            message = f"Afternoon Time In is available until {AFTERNOON_IN_CLOSE.strftime('%-I:%M %p')}."
        return "afternoon-in", allowed, message
    if record.check_out_at is None:
        return "afternoon-out", True, "Afternoon time-out is available."
    return None, False, "Attendance for today is already completed."


def _next_action_available_at(action: str | None, attendance_date: str, now: datetime | None = None) -> datetime | None:
    schedule = {
        "morning-in": MORNING_OPEN,
        "morning-out": MORNING_OUT_OPEN,
        "afternoon-in": AFTERNOON_IN_OPEN,
    }
    action_time = schedule.get(action)
    if action_time is None:
        return None
    available_at = datetime.combine(date.fromisoformat(attendance_date), action_time, ATTENDANCE_TZ)
    return available_at if (now or _now_manila()) < available_at else None


def _serialize(record: AttendanceRecord, now: datetime | None = None) -> dict:
    morning, afternoon = _recalculate(record)
    next_action, available, message = _next_action(record, now or _now_manila())
    return {
        "id": record.id,
        "email": record.email,
        "date": record.date,
        "check_in_at": record.check_in_at,
        "check_out_at": record.check_out_at,
        "morning_in_at": record.check_in_at,
        "morning_out_at": record.morning_out_at,
        "afternoon_in_at": record.afternoon_in_at,
        "afternoon_out_at": record.check_out_at,
        "morning_hours": morning,
        "afternoon_hours": afternoon,
        "total_hours_worked": record.hours_worked,
        "hours_worked": record.hours_worked,
        "regular_hours": record.regular_hours,
        "overtime_hours": record.overtime_hours,
        "arrival_status": record.arrival_status,
        "attendance_status": record.attendance_status,
        "next_action": next_action,
        "next_action_available": available,
        "next_action_available_at": _next_action_available_at(next_action, record.date, now),
        "next_action_message": message,
        "attendance_date": record.date,
        "timezone": ATTENDANCE_TIMEZONE,
        "manually_modified": record.manually_modified,
        "correction_note": record.correction_note,
        "corrected_at": record.corrected_at,
        "corrected_by_email": record.corrected_by_email,
    }


def _validate_transition(record: AttendanceRecord | None, action: str, now: datetime) -> None:
    current_time = now.timetz().replace(tzinfo=None)
    if record and record.check_out_at and not record.morning_out_at and not record.afternoon_in_at:
        raise HTTPException(status_code=400, detail="Attendance for today was already completed under the previous attendance format")
    if action == "morning-in":
        if record and record.check_in_at:
            raise HTTPException(status_code=400, detail="Morning time-in already recorded")
        if not MORNING_OPEN <= current_time < MORNING_CLOSE:
            raise HTTPException(
                status_code=400,
                detail=f"Morning Time In is only available from {MORNING_OPEN.strftime('%-I:%M %p')} to {MORNING_CLOSE.strftime('%-I:%M %p')} Philippine time.",
            )
        return
    if action == "afternoon-in" and (not record or not record.check_in_at):
        if record and record.afternoon_in_at:
            raise HTTPException(status_code=400, detail="Afternoon time-in already recorded")
        if not AFTERNOON_IN_OPEN <= current_time < AFTERNOON_IN_CLOSE:
            raise HTTPException(
                status_code=400,
                detail=f"Afternoon Time In is only available from {AFTERNOON_IN_OPEN.strftime('%-I:%M %p')} to {AFTERNOON_IN_CLOSE.strftime('%-I:%M %p')} Philippine time.",
            )
        return
    if action == "afternoon-out" and record and record.afternoon_in_at and not record.check_in_at:
        if record.check_out_at:
            raise HTTPException(status_code=400, detail="Attendance for today is already completed")
        return
    if not record or not record.check_in_at:
        raise HTTPException(status_code=400, detail="Morning Time In must be recorded first")
    if action == "morning-out":
        if record.morning_out_at:
            raise HTTPException(status_code=400, detail="Morning time-out already recorded")
        if current_time < MORNING_OUT_OPEN:
            raise HTTPException(status_code=400, detail=f"Morning time-out is available at {MORNING_OUT_OPEN.strftime('%-I:%M %p')}.")
        return
    if not record.morning_out_at:
        raise HTTPException(status_code=400, detail="Morning Time Out must be recorded first")
    if action == "afternoon-in":
        if record.afternoon_in_at:
            raise HTTPException(status_code=400, detail="Afternoon time-in already recorded")
        if not AFTERNOON_IN_OPEN <= current_time < AFTERNOON_IN_CLOSE:
            raise HTTPException(
                status_code=400,
                detail=f"Afternoon Time In is only available from {AFTERNOON_IN_OPEN.strftime('%-I:%M %p')} to {AFTERNOON_IN_CLOSE.strftime('%-I:%M %p')} Philippine time.",
            )
        return
    if not record.afternoon_in_at:
        raise HTTPException(status_code=400, detail="Afternoon Time In must be recorded first")
    if record.check_out_at:
        raise HTTPException(status_code=400, detail="Attendance for today is already completed")


def _record_action(action: str, payload: AttendanceLocation, current_user: User, db: Session) -> dict:
    if current_user.role != UserRole.staff:
        raise HTTPException(status_code=403, detail="Only staff can submit attendance actions")
    _enforce_geofence(db, payload)
    now = _now_manila()
    today = now.date().isoformat()
    record = db.scalar(
        select(AttendanceRecord)
        .where(and_(AttendanceRecord.email == current_user.email, AttendanceRecord.date == today))
        .with_for_update()
    )
    _validate_transition(record, action, now)
    if record is None:
        record = AttendanceRecord(email=current_user.email, date=today)
        db.add(record)
    if action == "morning-in":
        record.check_in_at = now
        record.check_in_lat, record.check_in_lng, record.check_in_accuracy_m = payload.lat, payload.lng, payload.accuracy
        record.arrival_status = "Late" if now.timetz().replace(tzinfo=None) >= LATE_AFTER else "On Time"
    elif action == "morning-out":
        record.morning_out_at = now
        record.morning_out_lat, record.morning_out_lng, record.morning_out_accuracy_m = payload.lat, payload.lng, payload.accuracy
    elif action == "afternoon-in":
        record.afternoon_in_at = now
        record.afternoon_in_lat, record.afternoon_in_lng, record.afternoon_in_accuracy_m = payload.lat, payload.lng, payload.accuracy
    else:
        record.check_out_at = now
        record.check_out_lat, record.check_out_lng, record.check_out_accuracy_m = payload.lat, payload.lng, payload.accuracy
    _recalculate(record)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="This attendance action was already recorded. Refresh and try again.")
    db.refresh(record)
    return _serialize(record, now)


@router.get("", response_model=list[AttendanceResponse])
def list_attendance(
    skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200),
    user_id: str | None = None, user_email: str | None = None, date: str | None = None,
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db),
):
    _require_attendance_role(current_user)
    query = select(AttendanceRecord).order_by(desc(AttendanceRecord.date), desc(AttendanceRecord.created_at))
    if current_user.role == UserRole.staff:
        query = query.where(AttendanceRecord.email == current_user.email)
    else:
        if user_id and not user_email:
            user = db.get(User, user_id)
            user_email = user.email if user else None
        if user_email:
            query = query.where(AttendanceRecord.email == user_email)
    if date:
        query = query.where(AttendanceRecord.date == date)
    return [_serialize(record) for record in db.scalars(query.offset(skip).limit(limit)).all()]


@router.get("/today", response_model=list[AttendanceResponse])
def today_attendance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_attendance_role(current_user)
    today = _now_manila().date().isoformat()
    query = select(AttendanceRecord).where(AttendanceRecord.date == today).order_by(AttendanceRecord.email)
    if current_user.role == UserRole.staff:
        query = query.where(AttendanceRecord.email == current_user.email)
    return [_serialize(record) for record in db.scalars(query).all()]


@router.get("/state/today")
def today_attendance_state(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != UserRole.staff:
        raise HTTPException(status_code=403, detail="This attendance state is available to staff only")
    now = _now_manila()
    attendance_date = now.date().isoformat()
    record = db.scalar(select(AttendanceRecord).where(
        and_(AttendanceRecord.email == current_user.email, AttendanceRecord.date == attendance_date)
    ))
    action, available, message = _next_action(record, now)
    return {
        "attendance_date": attendance_date,
        "timezone": ATTENDANCE_TIMEZONE,
        "next_action": action,
        "next_action_available": available,
        "next_action_available_at": _next_action_available_at(action, attendance_date, now),
        "next_action_message": message,
        "record": _serialize(record, now) if record else None,
    }


@router.get("/user/{user_id}", response_model=list[AttendanceResponse])
def get_user_attendance(user_id: str, skip: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_attendance_role(current_user)
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role == UserRole.staff and user.email != current_user.email:
        raise HTTPException(status_code=403, detail="Staff can only view their own attendance")
    records = db.scalars(select(AttendanceRecord).where(AttendanceRecord.email == user.email).order_by(desc(AttendanceRecord.date)).offset(skip).limit(limit)).all()
    return [_serialize(record) for record in records]


@router.get("/user/email/{email}", response_model=list[AttendanceResponse])
def get_user_attendance_by_email(email: str, skip: int = Query(0, ge=0), limit: int = Query(30, ge=1, le=100), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_attendance_role(current_user)
    if current_user.role == UserRole.staff and email.lower() != current_user.email.lower():
        raise HTTPException(status_code=403, detail="Staff can only view their own attendance")
    records = db.scalars(select(AttendanceRecord).where(AttendanceRecord.email == email).order_by(desc(AttendanceRecord.date)).offset(skip).limit(limit)).all()
    return [_serialize(record) for record in records]


@router.post("/morning-in", response_model=AttendanceResponse)
def morning_in(payload: AttendanceLocation, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _record_action("morning-in", payload, current_user, db)


@router.post("/morning-out", response_model=AttendanceResponse)
def morning_out(payload: AttendanceLocation, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _record_action("morning-out", payload, current_user, db)


@router.post("/afternoon-in", response_model=AttendanceResponse)
def afternoon_in(payload: AttendanceLocation, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _record_action("afternoon-in", payload, current_user, db)


@router.post("/afternoon-out", response_model=AttendanceResponse)
def afternoon_out(payload: AttendanceLocation, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _record_action("afternoon-out", payload, current_user, db)


@router.patch("/{record_id}/correction", response_model=AttendanceResponse)
def correct_attendance(record_id: str, payload: AttendanceCorrection, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_admin(current_user)
    record = db.scalar(select(AttendanceRecord).where(AttendanceRecord.id == record_id).with_for_update())
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    mapping = {
        "morning_in_at": "check_in_at", "morning_out_at": "morning_out_at",
        "afternoon_in_at": "afternoon_in_at", "afternoon_out_at": "check_out_at",
    }
    for field, target in mapping.items():
        if field in payload.model_fields_set:
            value = getattr(payload, field)
            if value is not None:
                local_value = _as_manila(value)
                if local_value.date().isoformat() != record.date:
                    raise HTTPException(status_code=400, detail=f"{field} must fall on the attendance date")
                setattr(record, target, local_value)
    timestamps = [record.check_in_at, record.morning_out_at, record.afternoon_in_at, record.check_out_at]
    present = [_as_manila(value) for value in timestamps if value is not None]
    if any(later < earlier for earlier, later in zip(present, present[1:])):
        raise HTTPException(status_code=400, detail="Attendance timestamps must follow the daily sequence")
    if record.check_in_at:
        record.arrival_status = "Late" if _as_manila(record.check_in_at).timetz().replace(tzinfo=None) >= LATE_AFTER else "On Time"
    record.manually_modified = True
    record.correction_note = payload.reason.strip()
    record.corrected_at = _now_manila()
    record.corrected_by_email = current_user.email
    _recalculate(record)
    db.commit()
    db.refresh(record)
    return _serialize(record)


@router.get("/{record_id}", response_model=AttendanceResponse)
def get_attendance_record(record_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _require_attendance_role(current_user)
    record = db.get(AttendanceRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    if current_user.role == UserRole.staff and record.email != current_user.email:
        raise HTTPException(status_code=403, detail="Staff can only view their own attendance")
    return _serialize(record)
