from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db import get_db
from app.models.stafftask import StaffTask, StaffTaskAssignee, TaskStatus
from app.models.staffcontribution import StaffContributionSnapshot
from app.schemas.stafftask import TaskCreate, TaskStatusUpdate, TaskOut
from datetime import datetime
from app.dependencies.auth import get_current_user, require_admin
from app.models.user import User, UserRole

router = APIRouter(prefix="/staff-tasks", tags=["staff-tasks"])


def get_visible_task(task_id: str, current_user: User, db: Session) -> StaffTask:
    task = db.get(StaffTask, task_id)
    can_view = task is not None and (
        current_user.role == UserRole.admin
        or any(a.staff_id == current_user.id for a in task.assignees)
    )
    if not can_view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return task


def serialize_task(task: StaffTask) -> dict:
    return {
        "id": task.id,
        "bookingId": task.booking_id,
        "projectName": task.project_name,
        "title": task.title,
        "description": task.description,
        "assignedStaffIds": [a.staff_id for a in task.assignees],
        "assignedStaffEmails": [
            a.staff.email for a in task.assignees if a.staff and a.staff.email
        ],
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
        },
    }


def upsert_contribution_snapshot(task: StaffTask, db: Session) -> None:
    contributor_ids = [a.staff_id for a in task.assignees]
    contributor_emails = [
        a.staff.email for a in task.assignees if a.staff and a.staff.email
    ]

    snapshot = db.scalars(
        select(StaffContributionSnapshot).where(
            StaffContributionSnapshot.task_id == str(task.id)
        )
    ).first()

    if snapshot is None:
        snapshot = StaffContributionSnapshot(
            task_id=str(task.id),
            project_name=task.project_name,
            task_title=task.title,
        )
        db.add(snapshot)

    snapshot.booking_id = task.booking_id
    snapshot.project_name = task.project_name
    snapshot.task_title = task.title
    snapshot.contributor_ids = contributor_ids
    snapshot.contributor_emails = contributor_emails
    snapshot.completed_at = datetime.utcnow()


@router.get("", response_model=list[TaskOut])
def list_staff_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List all tasks for admins and assigned tasks for staff."""
    query = select(StaffTask).order_by(desc(StaffTask.assigned_at))

    if current_user.role == UserRole.staff:
        query = query.join(StaffTaskAssignee).where(
            StaffTaskAssignee.staff_id == current_user.id
        )

    if status:
        query = query.where(StaffTask.status == status)

    query = query.offset(skip).limit(limit)
    tasks = db.scalars(query).all()

    return [serialize_task(task) for task in tasks]


@router.get("/{task_id}", response_model=TaskOut)
def get_staff_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a task only when it is assigned to the current staff member."""
    task = get_visible_task(task_id, current_user, db)
    return serialize_task(task)


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_staff_task(
    payload: TaskCreate,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Create a new staff task"""
    if payload.bookingId is not None:
        existing_task = db.scalars(
            select(StaffTask).where(StaffTask.booking_id == payload.bookingId)
        ).first()
        if existing_task is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A staff task already exists for this booking.",
            )

    # If location is not provided but bookingId is, try to copy location from the booking
    location_data = None
    if payload.location is not None:
        location_data = payload.location
    elif payload.bookingId is not None:
        from app.models.booking import Booking

        booking = db.get(Booking, payload.bookingId)
        if booking:
            location_data = type("LD", (), {})()
            location_data.province = booking.province
            location_data.municipality = booking.municipality
            location_data.barangay = booking.barangay
            location_data.house = booking.house

    if location_data is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Location is required"
        )

    task = StaffTask(
        booking_id=payload.bookingId,
        project_name=payload.projectName,
        title=payload.title,
        description=payload.description,
        due_date=payload.dueDate,
        province=location_data.province,
        municipality=location_data.municipality,
        barangay=location_data.barangay,
        house=location_data.house,
    )

    db.add(task)
    db.flush()

    from app.models.stafftask import StaffTaskAssignee

    for staff_id in payload.assignedStaffIds:
        assignee = StaffTaskAssignee(task_id=task.id, staff_id=staff_id)
        db.add(assignee)

    db.commit()
    db.refresh(task)

    return serialize_task(task)


@router.put("/{task_id}/status", response_model=TaskOut)
def update_staff_task_status(
    task_id: str,
    payload: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update task status"""
    task = get_visible_task(task_id, current_user, db)

    task.status = TaskStatus(payload.status)
    if task.status == TaskStatus.done:
        upsert_contribution_snapshot(task, db)
    db.commit()
    db.refresh(task)

    return serialize_task(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff_task(
    task_id: str,
    _admin=Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Delete a task"""
    task = db.get(StaffTask, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    db.delete(task)
    db.commit()
