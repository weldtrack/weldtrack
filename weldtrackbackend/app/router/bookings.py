from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db import get_db
from app.models.booking import Booking, BookingStatus, RecordMaterial
from app.models.service import Service
from app.models.customer_address import CustomerAddress
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
    MaterialCreate,
)
from app.router.auth import get_current_user
from app.models.user import User, UserRole
from app.models.inventory import InventoryItem, StockMovement, MovementType
from app.schemas.stafftask import TaskMaterialsCreate
from app.schemas.inventory import StockMovementResponse
from app.models.stafftask import TaskMaterialUsage, StaffTask
from app.core.config import FIXED_LABOR_RATE

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
    booking_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific booking by ID"""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )
    return booking


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new booking"""
    project_type = payload.project_type.strip()
    if not project_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project type is required",
        )

    available_service = db.scalar(select(Service).where(Service.name == project_type))
    if available_service is None:
        service_count = db.scalar(select(Service.id).limit(1))
        if service_count is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No services are currently available for booking",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected service is not available",
        )

    booking_data = payload.model_dump(exclude={"materials"}, exclude_none=True)
    booking_data["project_type"] = project_type

    if current_user.role == UserRole.customer:
        active_address = db.scalar(
            select(CustomerAddress).where(
                CustomerAddress.user_id == current_user.id,
                CustomerAddress.is_active.is_(True),
            )
        )
        if active_address is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please add and activate an address before creating a booking",
            )

        booking_data["email"] = current_user.email
        booking_data["country"] = active_address.country
        booking_data["region"] = active_address.region
        booking_data["province"] = active_address.province
        booking_data["municipality"] = active_address.municipality
        booking_data["barangay"] = active_address.barangay
        booking_data["house"] = active_address.house
        booking_data.setdefault("customer_name", current_user.email)

    booking = Booking(**booking_data)
    db.add(booking)
    db.flush()

    if payload.model_dump().get("materials"):
        for material_data in payload.materials:
            material = RecordMaterial(
                **material_data.model_dump(), booking_id=booking.id
            )
            db.add(material)

    db.commit()
    db.refresh(booking)
    return booking


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: str,
    payload: BookingUpdate,
    db: Session = Depends(get_db),
):
    """Update a booking"""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(booking, key):
            setattr(booking, key, value)

    db.commit()
    db.refresh(booking)
    return booking


@router.patch("/{booking_id}", response_model=BookingResponse)
def partial_update_booking(
    booking_id: str,
    payload: BookingUpdate,
    db: Session = Depends(get_db),
):
    """Partially update a booking"""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(booking, key):
            setattr(booking, key, value)

    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: str,
    db: Session = Depends(get_db),
):
    """Delete a booking"""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )

    db.delete(booking)
    db.commit()


@router.post("/{booking_id}/materials", response_model=list[StockMovementResponse])
def add_booking_materials(
    booking_id: str,
    payload: TaskMaterialsCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record materials used for a booking and persist a booking-linked material snapshot."""
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )
    if booking.status == BookingStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already completed",
        )

    existing_movements = db.scalars(
        select(StockMovement).where(
            StockMovement.booking_id == booking_id,
            StockMovement.task_id
            == (str(payload.taskId) if payload.taskId is not None else None),
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
    
    # Create TaskMaterialUsage record
    material_usage = TaskMaterialUsage(
        task_id=payload.taskId,
        booking_id=booking_id,
        submitted_by_staff_id=payload.submittedBy,
        before_image_url=payload.beforeImage,
        after_image_url=payload.afterImage,
        labor_hours=payload.laborHours,
    )
    db.add(material_usage)
    
    # Calculate and update labor cost
    task = db.get(StaffTask, payload.taskId)
    if task:
        staff_count = len(task.assignees)
        service = db.scalar(select(Service).where(Service.name == booking.project_type))
        labor_price = service.price if service else 0
        booking.estimated_cost = payload.laborHours * staff_count * labor_price
    
    for line in payload.lines:
        item = db.get(InventoryItem, line.itemId)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory item {line.itemId} not found",
            )

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
