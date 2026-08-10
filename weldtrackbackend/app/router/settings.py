from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from app.db import get_db
from app.models.attendance_site import AttendanceSite
from app.models.user import User, UserRole
from app.schemas.settings import AttendanceSiteIn, AttendanceSiteResponse
from app.router.auth import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage the attendance location",
        )
    return current_user


@router.get("/attendance-location", response_model=AttendanceSiteResponse)
def get_attendance_location(
    _admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Return the configured attendance site, if one has been set."""
    site = db.scalar(select(AttendanceSite).order_by(desc(AttendanceSite.updated_at)))
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No attendance location has been set yet",
        )
    return site


@router.post("/attendance-location", response_model=AttendanceSiteResponse)
def set_attendance_location(
    payload: AttendanceSiteIn,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Create or update the single fixed attendance site."""
    site = db.scalar(select(AttendanceSite).order_by(desc(AttendanceSite.updated_at)))
    if site:
        site.lat = payload.lat
        site.lng = payload.lng
        site.radius_meters = payload.radius_meters
    else:
        site = AttendanceSite(
            lat=payload.lat,
            lng=payload.lng,
            radius_meters=payload.radius_meters,
        )
        db.add(site)

    db.commit()
    db.refresh(site)
    return site
