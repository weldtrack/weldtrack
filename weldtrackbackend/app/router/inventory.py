from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db import get_db
from app.models.inventory import InventoryItem, StockMovement, MovementType
from app.models.stafftask import StaffTask
from app.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    StockMovementResponse,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("", response_model=list[InventoryItemResponse])
def list_inventory(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get all inventory items"""
    query = select(InventoryItem).offset(skip).limit(limit)
    items = db.scalars(query).all()
    return items


@router.get("/{item_id}", response_model=InventoryItemResponse)
def get_inventory_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific inventory item"""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.post("", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
def create_inventory_item(
    payload: InventoryItemCreate,
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
    item_id: int,
    payload: InventoryItemUpdate,
    db: Session = Depends(get_db),
):
    """Update an inventory item"""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(item, key):
            setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.patch("/{item_id}", response_model=InventoryItemResponse)
def partial_update_inventory_item(
    item_id: int,
    payload: InventoryItemUpdate,
    db: Session = Depends(get_db),
):
    """Partially update an inventory item"""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    old_quantity = item.quantity or 0
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(item, key):
            setattr(item, key, value)
    
    new_quantity = item.quantity or 0
    if old_quantity != new_quantity:
        quantity_delta = new_quantity - old_quantity
        movement_type = MovementType.stock_in if quantity_delta > 0 else MovementType.stock_out
        
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
    item_id: int,
    db: Session = Depends(get_db),
):
    """Delete an inventory item"""
    item = db.get(InventoryItem, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    db.delete(item)
    db.commit()


@router.get("/movements/history", response_model=list[StockMovementResponse])
def get_stock_movements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    item_id: int | None = None,
    booking_id: int | None = None,
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
    task_ids: list[UUID] = []
    for movement in movements:
        if not movement.task_id:
            continue
        try:
            task_ids.append(UUID(movement.task_id))
        except ValueError:
            continue

    tasks_by_id: dict[str, StaffTask] = {}
    if task_ids:
        tasks = db.scalars(select(StaffTask).where(StaffTask.id.in_(task_ids))).all()
        tasks_by_id = {str(task.id): task for task in tasks}

    return [
        {
            "id": movement.id,
            "item_id": movement.item_id,
            "item_name": movement.item_name,
            "quantity": movement.quantity,
            "type": movement.type.value,
            "timestamp": movement.timestamp,
            "booking_id": movement.booking_id,
            "task_id": movement.task_id,
            "team_emails": [
                assignee.staff.email
                for assignee in tasks_by_id.get(movement.task_id, []).assignees
                if assignee.staff and assignee.staff.email
            ] if movement.task_id and movement.task_id in tasks_by_id else [],
        }
        for movement in movements
    ]
