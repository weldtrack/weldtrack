from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc, func
from app.db import get_db
from app.models.booking import Booking, BookingStatus, RecordMaterial
from app.models.service import Service
from app.models.customer_address import CustomerAddress
from app.schemas.booking import (
    BookingCreate,
    BookingUpdate,
    BookingResponse,
)
from app.models.user import User, UserRole
from app.models.inventory import InventoryItem, StockMovement, MovementType
from app.schemas.stafftask import TaskMaterialsCreate
from app.schemas.inventory import StockMovementResponse
from app.models.stafftask import TaskMaterialUsage, StaffTask, StaffTaskAssignee
from app.dependencies.auth import get_current_user, require_admin

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _staff_booking_ids_query(user_id: str):
    return (
        select(StaffTask.booking_id)
        .join(StaffTaskAssignee, StaffTaskAssignee.task_id == StaffTask.id)
        .where(
            StaffTaskAssignee.staff_id == user_id,
            StaffTask.booking_id.is_not(None),
        )
    )


def _can_view_booking(booking: Booking, current_user: User, db: Session) -> bool:
    if current_user.role == UserRole.admin:
        return True
    if current_user.role == UserRole.customer:
        return bool(
            booking.email
            and booking.email.casefold() == current_user.email.casefold()
        )
    return db.scalar(
        select(StaffTaskAssignee.staff_id)
        .join(StaffTask, StaffTask.id == StaffTaskAssignee.task_id)
        .where(
            StaffTaskAssignee.staff_id == current_user.id,
            StaffTask.booking_id == booking.id,
        )
        .limit(1)
    ) is not None


def _get_visible_booking(
    booking_id: str, current_user: User, db: Session
) -> Booking:
    booking = db.get(Booking, booking_id)
    # Return the same response for missing and inaccessible records so callers
    # cannot use this endpoint to discover another customer's booking IDs.
    if booking is None or not _can_view_booking(booking, current_user, db):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found"
        )
    return booking


def _apply_booking_update(
    booking: Booking,
    payload: BookingUpdate,
    current_user: User,
) -> None:
    changes = payload.model_dump(exclude_unset=True)
    # These values are derived from persisted labor and material records. They
    # must never be accepted from a browser-provided total.
    for derived_field in (
        "estimated_cost",
        "actual_labor_cost",
        "material_cost",
        "total_price",
    ):
        changes.pop(derived_field, None)
    if current_user.role == UserRole.customer:
        allowed_fields = {"status", "cancel_reason", "cancelled_by"}
        if set(changes) - allowed_fields:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customers may only cancel their own pending bookings",
            )
        if (
            booking.status != BookingStatus.pending
            or changes.get("status") != BookingStatus.cancelled
            or changes.get("cancelled_by") != "customer"
            or not str(changes.get("cancel_reason") or "").strip()
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customers may only cancel their own pending bookings",
            )
    elif current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators may update bookings",
        )

    for key, value in changes.items():
        if hasattr(booking, key):
            setattr(booking, key, value)


def _recalculate_booking_totals(booking: Booking) -> None:
    booking.material_cost = sum(
        float(line.subtotal or 0) for line in (booking.materials or [])
    )
    labor_cost = (
        float(booking.actual_labor_cost)
        if booking.actual_labor_cost is not None
        else float(booking.estimated_cost or 0)
    )
    booking.total_price = labor_cost + float(booking.material_cost or 0)


def _calculate_service_labor_cost(
    service: Service | None,
    labor_hours: float | None,
) -> float:
    if not service:
        return 0.0
    pricing_type = getattr(service, "pricing_type", "hourly") or "hourly"
    fixed_price = float(service.price_fixed or 0.0)
    hourly_rate = float(service.price_hour or 0.0)
    hours = float(labor_hours or 0.0)

    if pricing_type == "fixed":
        return fixed_price
    elif pricing_type == "hybrid":
        return fixed_price + (hours * hourly_rate)
    else:  # "hourly"
        return hours * hourly_rate


def _recalculate_booking_estimate(booking: Booking, db: Session) -> None:
    service = db.scalar(select(Service).where(Service.name == booking.project_type))
    if not service:
        return
    pricing_type = getattr(service, "pricing_type", "hourly") or "hourly"
    if pricing_type == "fixed":
        booking.estimated_cost = float(service.price_fixed or 0.0)
    else:
        if booking.estimated_labor_hours is None:
            return
        booking.estimated_cost = _calculate_service_labor_cost(
            service, booking.estimated_labor_hours
        )


@router.get("", response_model=list[BookingResponse])
def list_bookings(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List bookings visible to the current user."""
    query = select(Booking).order_by(desc(Booking.created_date))

    if current_user.role == UserRole.customer:
        query = query.where(func.lower(Booking.email) == current_user.email.lower())
    elif current_user.role == UserRole.staff:
        query = query.where(Booking.id.in_(_staff_booking_ids_query(current_user.id)))

    if status:
        query = query.where(Booking.status == status)

    query = query.offset(skip).limit(limit)
    bookings = db.scalars(query).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a booking only when it is visible to the current user."""
    return _get_visible_booking(booking_id, current_user, db)


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    payload: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new booking"""
    if current_user.role == UserRole.staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff cannot create customer bookings",
        )
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

    # Duplicate Booking Guard: Check if customer already has an active booking for this service
    existing_active = db.scalar(
        select(Booking.id).where(
            Booking.email == current_user.email,
            func.lower(Booking.project_type) == project_type.lower(),
            Booking.status.in_([BookingStatus.pending, BookingStatus.confirmed]),
        )
    )
    if existing_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You already have an active booking for '{project_type}'. Please wait for your existing booking to be completed or cancelled before booking again.",
        )

    booking_data = payload.model_dump(exclude={"materials"}, exclude_none=True)
    booking_data["project_type"] = project_type
    for derived_field in (
        "estimated_cost",
        "actual_labor_cost",
        "material_cost",
        "total_price",
    ):
        booking_data.pop(derived_field, None)

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
        booking_data["status"] = BookingStatus.pending
        booking_data["country"] = active_address.country
        booking_data["region"] = active_address.region
        booking_data["province"] = active_address.province
        booking_data["municipality"] = active_address.municipality
        booking_data["barangay"] = active_address.barangay
        booking_data["house"] = active_address.house
        booking_data.setdefault("customer_name", current_user.email)

    booking = Booking(**booking_data)
    _recalculate_booking_estimate(booking, db)
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a booking"""
    booking = _get_visible_booking(booking_id, current_user, db)
    _apply_booking_update(booking, payload, current_user)
    _recalculate_booking_estimate(booking, db)
    if booking.status == BookingStatus.completed:
        _recalculate_booking_totals(booking)

    db.commit()
    db.refresh(booking)
    return booking


@router.patch("/{booking_id}", response_model=BookingResponse)
def partial_update_booking(
    booking_id: str,
    payload: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Partially update a booking"""
    booking = _get_visible_booking(booking_id, current_user, db)
    _apply_booking_update(booking, payload, current_user)
    _recalculate_booking_estimate(booking, db)
    if booking.status == BookingStatus.completed:
        _recalculate_booking_totals(booking)

    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: str,
    _admin: User = Depends(require_admin),
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
    if current_user.role == UserRole.customer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires staff or admin privileges",
        )
    booking = _get_visible_booking(booking_id, current_user, db)
    if booking.status == BookingStatus.completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking is already completed",
        )

    task = db.get(StaffTask, payload.taskId)
    if task is None or task.booking_id != booking_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task does not belong to this booking",
        )
    if current_user.role == UserRole.staff and not any(
        assignee.staff_id == current_user.id for assignee in task.assignees
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This task is not assigned to the current staff member",
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
        submitted_by_staff_id=current_user.id,
        before_image_url=payload.beforeImage,
        after_image_url=payload.afterImage,
        labor_hours=payload.laborHours,
    )
    db.add(material_usage)
    
    # Calculate and update labor cost
    service = db.scalar(select(Service).where(Service.name == booking.project_type))
    booking.actual_labor_cost = _calculate_service_labor_cost(
        service, payload.laborHours
    )
    
    for line in payload.lines:
        item = db.get(InventoryItem, line.itemId)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inventory item {line.itemId} not found",
            )
        if item.is_archived:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"{item.name} is archived and cannot be used",
            )

        qty = int(line.quantity)
        if qty <= 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Quantity for {item.name} must be greater than zero",
            )
        if qty > int(item.quantity or 0):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Insufficient stock for {item.name}: "
                    f"{int(item.quantity or 0)} available"
                ),
            )
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

        item.quantity -= qty
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
