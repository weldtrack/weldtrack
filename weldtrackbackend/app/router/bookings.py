from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db import get_db
from app.models.booking import Booking, BookingStatus, RecordMaterial
from app.schemas.booking import BookingCreate, BookingUpdate, BookingResponse, MaterialCreate
from app.router.user.auth import get_current_user
from app.models.user import User
from app.models.inventory import InventoryItem, StockMovement, MovementType
from app.schemas.stafftask import TaskMaterialsCreate
from app.schemas.inventory import StockMovementResponse

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
    
    if payload.model_dump().get("materials"):
        for material_data in payload.materials:
            material = RecordMaterial(**material_data.model_dump(), booking_id=booking.id)
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



@router.post("/{booking_id}/materials", response_model=list[StockMovementResponse])
def add_booking_materials(
    booking_id: int,
    payload: TaskMaterialsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record materials used for a booking and persist a booking-linked material snapshot."""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    if booking.status == BookingStatus.completed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Booking is already completed")

    existing_movements = db.scalars(
        select(StockMovement).where(
            StockMovement.booking_id == booking_id,
            StockMovement.task_id == (str(payload.taskId) if payload.taskId is not None else None),
            StockMovement.type == MovementType.stock_out,
        )
    ).all()

    for movement in existing_movements:
        item = db.get(InventoryItem, movement.item_id)
        if item:
            item.quantity = int(item.quantity or 0) + int(movement.quantity or 0)
            db.add(item)
        db.delete(movement)

    for material in list(booking.materials or []):
        db.delete(material)

    created: list[StockMovement] = []

    for line in payload.lines:
        item = db.get(InventoryItem, line.itemId)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Inventory item {line.itemId} not found")

        qty = int(line.quantity)
        unit_price = float(item.unit_price or 0)
        subtotal = qty * unit_price

        material_record = RecordMaterial(
            booking_id=booking_id,
            item_id=str(item.id),
            name=item.name,
            qty=qty,
            unit_price=unit_price,
            subtotal=subtotal,
            is_temp=0,
        )
        db.add(material_record)

        movement = StockMovement(
            item_id=item.id,
            item_name=item.name,
            quantity=qty,
            type=MovementType.stock_out,
            booking_id=booking_id,
            task_id=str(payload.taskId) if payload.taskId is not None else None,
        )
        db.add(movement)

        item.quantity = max(0, item.quantity - qty)
        db.add(item)
        created.append(movement)

    if payload.beforeImage:
        booking.before_images = [payload.beforeImage]
    if payload.afterImage:
        booking.after_images = [payload.afterImage]
    db.add(booking)

    db.commit()

    for m in created:
        db.refresh(m)

    return created
