from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db import get_db
from app.models.booking import Booking, BookingStatus, BookingMaterial
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse, MaterialCreate
from app.router.user.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingResponse])
def list_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str | None = None,
    db: Session = Depends(get_db),
):
    """Get all bookings with optional filtering"""
    query = select(Booking).order_by(desc(Booking.created_date))
    
    if status:
        query = query.where(Booking.status == status)
    
    query = query.offset(skip).limit(limit)
    bookings = db.scalars(query).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific booking by ID"""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    return booking


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
):
    """Create a new booking"""
    booking = Booking(**payload.model_dump(exclude={"materials"}))
    db.add(booking)
    db.flush()
    
    # Add materials if provided
    if payload.model_dump().get("materials"):
        for material_data in payload.materials:
            material = BookingMaterial(**material_data.model_dump(), booking_id=booking.id)
            db.add(material)
    
    db.commit()
    db.refresh(booking)
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int,
    payload: BookingUpdate,
    db: Session = Depends(get_db),
):
    """Update a booking"""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Update fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(booking, key):
            setattr(booking, key, value)
    
    db.commit()
    db.refresh(booking)
    return booking


@router.patch("/{booking_id}", response_model=BookingResponse)
def partial_update_booking(
    booking_id: int,
    payload: BookingUpdate,
    db: Session = Depends(get_db),
):
    """Partially update a booking"""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Update fields
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(booking, key):
            setattr(booking, key, value)
    
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
):
    """Delete a booking"""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    db.delete(booking)
    db.commit()
