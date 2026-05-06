from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from uuid import UUID
from app.db import get_db
from app.models.stafftask import StaffTask, TaskStatus
from app.schemas.stafftask import TaskCreate, TaskStatusUpdate, TaskOut
from datetime import datetime

router = APIRouter(prefix="/staff-tasks", tags=["staff-tasks"])


@router.get("", response_model=list[TaskOut])
def list_staff_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = None,
    db: Session = Depends(get_db),
):
    """Get all staff tasks"""
    query = select(StaffTask).order_by(desc(StaffTask.assigned_at))
    
    if status:
        query = query.where(StaffTask.status == status)
    
    query = query.offset(skip).limit(limit)
    tasks = db.scalars(query).all()
    
    # Format response
    return [
        {
            "id": task.id,
            "projectName": task.project_name,
            "title": task.title,
            "description": task.description,
            "assignedStaffIds": [a.staff_id for a in task.assignees],
            "assignedAt": task.assigned_at,
            "dueDate": task.due_date,
            "status": task.status.value,
            "location": {
                "country": task.country,
                "region": task.region,
                "province": task.province,
                "municipality": task.municipality,
                "barangay": task.barangay,
                "house": task.house,
            }
        }
        for task in tasks
    ]


@router.get("/{task_id}", response_model=TaskOut)
def get_staff_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    """Get a specific task"""
    task = db.get(StaffTask, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return {
        "id": task.id,
        "projectName": task.project_name,
        "title": task.title,
        "description": task.description,
        "assignedStaffIds": [a.staff_id for a in task.assignees],
        "assignedAt": task.assigned_at,
        "dueDate": task.due_date,
        "status": task.status.value,
        "location": {
            "country": task.country,
            "region": task.region,
            "province": task.province,
            "municipality": task.municipality,
            "barangay": task.barangay,
            "house": task.house,
        }
    }


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_staff_task(
    payload: TaskCreate,
    db: Session = Depends(get_db),
):
    """Create a new staff task"""
    task = StaffTask(
        project_name=payload.projectName,
        title=payload.title,
        description=payload.description,
        due_date=payload.dueDate,
        province=payload.location.province,
        municipality=payload.location.municipality,
        barangay=payload.location.barangay,
        house=payload.location.house,
    )
    
    db.add(task)
    db.flush()
    
    # Add assignees
    from app.models.stafftask import StaffTaskAssignee
    for staff_id in payload.assignedStaffIds:
        assignee = StaffTaskAssignee(task_id=task.id, staff_id=staff_id)
        db.add(assignee)
    
    db.commit()
    db.refresh(task)
    
    return {
        "id": task.id,
        "projectName": task.project_name,
        "title": task.title,
        "description": task.description,
        "assignedStaffIds": payload.assignedStaffIds,
        "assignedAt": task.assigned_at,
        "dueDate": task.due_date,
        "status": task.status.value,
        "location": {
            "country": task.country,
            "region": task.region,
            "province": task.province,
            "municipality": task.municipality,
            "barangay": task.barangay,
            "house": task.house,
        }
    }


@router.put("/{task_id}/status", response_model=TaskOut)
def update_staff_task_status(
    task_id: UUID,
    payload: TaskStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update task status"""
    task = db.get(StaffTask, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    task.status = TaskStatus(payload.status)
    db.commit()
    db.refresh(task)
    
    return {
        "id": task.id,
        "projectName": task.project_name,
        "title": task.title,
        "description": task.description,
        "assignedStaffIds": [a.staff_id for a in task.assignees],
        "assignedAt": task.assigned_at,
        "dueDate": task.due_date,
        "status": task.status.value,
        "location": {
            "country": task.country,
            "region": task.region,
            "province": task.province,
            "municipality": task.municipality,
            "barangay": task.barangay,
            "house": task.house,
        }
    }


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_task(
    task_id: UUID,
    db: Session = Depends(get_db),
):
    """Delete a task"""
    task = db.get(StaffTask, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    db.delete(task)
    db.commit()
