from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status, Query

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, desc, or_
from app.db import get_db
from app.models.booking import Booking
from app.models.inventory import InventoryItem, StockMovement, MovementType
from app.models.stafftask import StaffTask, StaffTaskAssignee, TaskMaterialUsage
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    StockMovementResponse,
)
from app.dependencies.auth import require_admin

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryItemResponse])
def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    archived: bool = Query(False),
    db: Session = Depends(get_db),
):
    """Get active or archived inventory items."""
    query = (
        select(InventoryItem)
        .where(InventoryItem.is_archived.is_(archived))
        .order_by(desc(InventoryItem.date_added))
        .offset(skip)
        .limit(limit)
    )
    items = db.scalars(query).all()
    return items


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(
    item_id: str,
    db: Session = Depends(get_db),
):
    """Get a specific inventory item"""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return item


@router.post(
    "", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED
)
def create_inventory_item(
    payload: InventoryItemCreate,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new inventory item"""
    item = InventoryItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
def update_inventory_item(
    item_id: str,
    payload: InventoryItemUpdate,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Update an inventory item"""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    if item.is_archived:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Restore this item before updating it",
        )

    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(item, key):
            setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=InventoryItemResponse)
def partial_update_inventory_item(
    item_id: str,
    payload: InventoryItemUpdate,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Partially update an inventory item"""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    if item.is_archived:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Restore this item before updating it",
        )

    old_quantity = item.quantity or 0

    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(item, key):
            setattr(item, key, value)

    new_quantity = item.quantity or 0
    if old_quantity != new_quantity:
        quantity_delta = new_quantity - old_quantity
        movement_type = (
            MovementType.stock_in if quantity_delta > 0 else MovementType.stock_out
        )

        movement = StockMovement(
            item_id=item.id,
            item_name=item.name,
            quantity=abs(quantity_delta),
            type=movement_type,
        )
        db.add(movement)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_inventory_item(
    item_id: str,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Archive an inventory item (kept for backwards-compatible clients)."""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    item.is_archived = True
    item.archived_at = datetime.now(timezone.utc)
    db.commit()


@router.post("/{item_id}/archive", response_model=InventoryItemResponse)
def archive_inventory_item(
    item_id: str,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Move an active inventory item to the archive."""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if item.is_archived:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item is already archived")
    item.is_archived = True
    item.archived_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{item_id}/restore", response_model=InventoryItemResponse)
def restore_inventory_item(
    item_id: str,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Restore an archived inventory item to active inventory."""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if not item.is_archived:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Item is already active")
    item.is_archived = False
    item.archived_at = None
    db.commit()
    db.refresh(item)
    return item


@router.get("/movements/history", response_model=list[StockMovementResponse])
def get_stock_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    item_id: str | None = None,
    booking_id: str | None = None,
    task_id: str | None = None,
    db: Session = Depends(get_db),
):
    """Get stock movement history"""
    query = select(StockMovement).order_by(desc(StockMovement.timestamp))

    if item_id:
        query = query.where(StockMovement.item_id == item_id)
    if booking_id:
        query = query.where(StockMovement.booking_id == booking_id)
    if task_id:
        query = query.where(StockMovement.task_id == task_id)

    query = query.offset(skip).limit(limit)
    movements = db.scalars(query).all()

    # Collect IDs to batch load linked tasks, bookings, and material usages
    task_ids: set[str] = {m.task_id for m in movements if m.task_id}
    booking_ids: set[str] = {m.booking_id for m in movements if m.booking_id}

    # 1. Fetch bookings to retrieve project_type (service name)
    bookings_by_id: dict[str, Booking] = {}
    if booking_ids:
        b_list = db.scalars(select(Booking).where(Booking.id.in_(booking_ids))).all()
        bookings_by_id = {str(b.id): b for b in b_list}

    # 2. Fetch staff tasks (with assignees & staff eager loaded)
    tasks_by_id: dict[str, StaffTask] = {}
    tasks_by_booking_id: dict[str, StaffTask] = {}
    if task_ids or booking_ids:
        t_conditions = []
        if task_ids:
            t_conditions.append(StaffTask.id.in_(task_ids))
        if booking_ids:
            t_conditions.append(StaffTask.booking_id.in_(booking_ids))
        t_list = db.scalars(
            select(StaffTask)
            .options(
                joinedload(StaffTask.assignees).joinedload(StaffTaskAssignee.staff)
            )
            .where(or_(*t_conditions))
        ).unique().all()
        for t in t_list:
            tasks_by_id[str(t.id)] = t
            if t.booking_id:
                tasks_by_booking_id[str(t.booking_id)] = t

    # 3. Fetch material usages to identify who submitted the usage
    usages_by_task_id: dict[str, TaskMaterialUsage] = {}
    usages_by_booking_id: dict[str, TaskMaterialUsage] = {}
    if task_ids or booking_ids:
        u_conditions = []
        if task_ids:
            u_conditions.append(TaskMaterialUsage.task_id.in_(task_ids))
        if booking_ids:
            u_conditions.append(TaskMaterialUsage.booking_id.in_(booking_ids))
        u_list = db.scalars(
            select(TaskMaterialUsage)
            .options(joinedload(TaskMaterialUsage.submitted_by_staff))
            .where(or_(*u_conditions))
        ).unique().all()
        for u in u_list:
            if u.task_id:
                usages_by_task_id[str(u.task_id)] = u
            if u.booking_id:
                usages_by_booking_id[str(u.booking_id)] = u

    # Build response records ensuring team and staff who used the service is ALWAYS included
    result = []
    for movement in movements:
        booking = bookings_by_id.get(movement.booking_id) if movement.booking_id else None
        task = None
        if movement.task_id and movement.task_id in tasks_by_id:
            task = tasks_by_id[movement.task_id]
        elif movement.booking_id and movement.booking_id in tasks_by_booking_id:
            task = tasks_by_booking_id[movement.booking_id]

        usage = None
        if movement.task_id and movement.task_id in usages_by_task_id:
            usage = usages_by_task_id[movement.task_id]
        elif movement.booking_id and movement.booking_id in usages_by_booking_id:
            usage = usages_by_booking_id[movement.booking_id]

        # Determine service name
        service_name = None
        if booking and booking.project_type:
            service_name = booking.project_type
        elif task and task.project_name:
            service_name = task.project_name
        elif movement.type == MovementType.stock_in:
            service_name = "Warehouse Replenishment"
        else:
            service_name = "Inventory Adjustment"

        # Determine team emails and staff
        team_emails: list[str] = []
        if task:
            for assignee in task.assignees:
                if assignee.staff and assignee.staff.email and assignee.staff.email not in team_emails:
                    team_emails.append(assignee.staff.email)

        recorded_by = None
        if usage and usage.submitted_by_staff and usage.submitted_by_staff.email:
            recorded_by = usage.submitted_by_staff.email
            if recorded_by not in team_emails:
                team_emails.append(recorded_by)

        # Ensure team/staff is NEVER empty
        if not team_emails:
            if movement.booking_id or movement.task_id:
                team_emails = ["Staff Field Team"]
                recorded_by = recorded_by or "Assigned Staff"
            elif movement.type == MovementType.stock_in:
                team_emails = ["Admin / Warehouse Manager"]
                recorded_by = recorded_by or "Admin"
            else:
                team_emails = ["Admin / Inventory Team"]
                recorded_by = recorded_by or "Admin"
        else:
            recorded_by = recorded_by or team_emails[0]

        result.append({
            "id": movement.id,
            "item_id": movement.item_id,
            "item_name": movement.item_name,
            "quantity": movement.quantity,
            "type": movement.type.value,
            "timestamp": movement.timestamp,
            "booking_id": movement.booking_id,
            "task_id": movement.task_id,
            "service_name": service_name,
            "team_emails": team_emails,
            "recorded_by": recorded_by,
        })

    return result
