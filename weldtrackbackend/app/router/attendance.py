from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, and_
from datetime import datetime, timezone
from app.db import get_db
from app.models.attendance import AttendanceRecord
from app.models.attendance_site import AttendanceSite
from app.models.user import User, UserRole
from app.schemas.attendance import (
    AttendanceCheckIn,
    AttendanceCheckOut,
    AttendanceResponse,
)
from app.router.auth import get_current_user
from app.geo import haversine_meters

router = APIRouter(prefix="/attendance", tags=["attendance"])

# Mirrors the frontend's own GPS-accuracy gate, but this is the copy that
# actually matters since the client can't be trusted to enforce itself.
MAX_CHECK_IN_ACCURACY_M = 75


def _get_configured_site(db: Session) -> AttendanceSite | None:
    return db.scalar(select(AttendanceSite).order_by(desc(AttendanceSite.updated_at)))


def _enforce_geofence(db: Session, lat: float | None, lng: float | None, accuracy: float | None) -> None:
    """Raise a 400 if a site is configured and the given point falls outside it.

    No-ops if the admin hasn't configured a site yet, so nobody is locked
    out of check-in before that's been set up.
    """
    site = _get_configured_site(db)
    if not site:
        return

    if lat is None or lng is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Location is required to check in or out at this site",
        )

    if accuracy is not None and accuracy > MAX_CHECK_IN_ACCURACY_M:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Location signal is too weak (±{round(accuracy)}m). "
                "Move to an open area and try again."
            ),
        )

    distance = haversine_meters(site.lat, site.lng, lat, lng)
    if distance > site.radius_meters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"You're {round(distance)}m from the job site — check-in "
                f"requires being within {round(site.radius_meters)}m."
            ),
        )


@router.get("", response_model=list[AttendanceResponse])
def list_attendance(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: int | None = None,
    user_email: str | None = None,
    date: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get attendance records. Staff can only see their own."""
    query = select(AttendanceRecord).order_by(desc(AttendanceRecord.created_at))

    if current_user.role == UserRole.staff:
        query = query.where(AttendanceRecord.email == current_user.email)
    elif user_id and not user_email:
        user = db.get(User, user_id)
        if user:
            user_email = user.email

    if user_email and current_user.role == UserRole.admin:
        query = query.where(AttendanceRecord.email == user_email)

    if date:
        query = query.where(AttendanceRecord.date == date)

    query = query.offset(skip).limit(limit)
    records = db.scalars(query).all()
    return records


@router.get("/user/{user_id}", response_model=list[AttendanceResponse])
def get_user_attendance(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get attendance records for a specific user"""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    query = (
        select(AttendanceRecord)
        .where(AttendanceRecord.email == user.email)
        .order_by(desc(AttendanceRecord.date))
        .offset(skip)
        .limit(limit)
    )
    records = db.scalars(query).all()
    return records


@router.get("/user/email/{email}", response_model=list[AttendanceResponse])
def get_user_attendance_by_email(
    email: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get attendance records for a specific user by email"""
    query = (
        select(AttendanceRecord)
        .where(AttendanceRecord.email == email)
        .order_by(desc(AttendanceRecord.date))
        .offset(skip)
        .limit(limit)
    )
    records = db.scalars(query).all()
    return records


@router.post("/check-in", response_model=AttendanceResponse)
def check_in(
    payload: AttendanceCheckIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check in for the current user, enforcing the configured job-site radius."""
    if current_user.role != UserRole.staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can check in",
        )

    _enforce_geofence(db, payload.lat, payload.lng, payload.accuracy)

    today = datetime.now(timezone.utc).date().isoformat()

    existing = db.scalar(
        select(AttendanceRecord).where(
            and_(
                AttendanceRecord.email == current_user.email,
                AttendanceRecord.date == today,
            )
        )
    )

    if existing and existing.check_in_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked in today",
        )

    record = AttendanceRecord(
        email=current_user.email,
        date=today,
        check_in_at=datetime.now(timezone.utc),
        check_in_lat=payload.lat,
        check_in_lng=payload.lng,
        check_in_accuracy_m=payload.accuracy,
    )

    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/check-out", response_model=AttendanceResponse)
def check_out(
    payload: AttendanceCheckOut,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check out for the current user, enforcing the configured job-site radius."""
    if current_user.role != UserRole.staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only staff can check out",
        )

    _enforce_geofence(db, payload.lat, payload.lng, payload.accuracy)

    today = datetime.now(timezone.utc).date().isoformat()

    record = db.scalar(
        select(AttendanceRecord).where(
            and_(
                AttendanceRecord.email == current_user.email,
                AttendanceRecord.date == today,
            )
        )
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No check-in found for today",
        )

    if record.check_out_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already checked out today",
        )

    check_out_time = datetime.now(timezone.utc)
    record.check_out_at = check_out_time
    record.check_out_lat = payload.lat
    record.check_out_lng = payload.lng
    record.check_out_accuracy_m = payload.accuracy

    if record.check_in_at:
        hours = (check_out_time - record.check_in_at).total_seconds() / 3600
        record.hours_worked = round(hours, 2)
        record.regular_hours = min(hours, 8)  # 8-hour workday
        record.overtime_hours = max(0, hours - 8)

    db.commit()
    db.refresh(record)
    return record


@router.get("/{record_id}", response_model=AttendanceResponse)
def get_attendance_record(
    record_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific attendance record"""
    record = db.get(AttendanceRecord, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record not found",
        )
    return record