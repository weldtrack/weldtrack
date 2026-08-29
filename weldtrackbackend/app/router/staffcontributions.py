from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.staffcontribution import StaffContributionSnapshot
from app.models.stafftask import StaffTask, TaskStatus
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole

router = APIRouter(prefix="/staff-contributions", tags=["staff-contributions"])


def backfill_missing_snapshots(db: Session) -> None:
    done_tasks = db.scalars(
        select(StaffTask).where(StaffTask.status == TaskStatus.done)
    ).all()

    for task in done_tasks:
        existing = db.scalars(
            select(StaffContributionSnapshot).where(
                StaffContributionSnapshot.task_id == str(task.id)
            )
        ).first()
        if existing is not None:
            continue

        db.add(
            StaffContributionSnapshot(
                task_id=str(task.id),
                project_name=task.project_name,
                task_title=task.title,
                contributor_ids=[a.staff_id for a in task.assignees],
                contributor_emails=[
                    a.staff.email for a in task.assignees if a.staff and a.staff.email
                ],
                completed_at=task.assigned_at,
            )
        )

    db.commit()


@router.get("")
def list_staff_contributions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    backfill_missing_snapshots(db)

    snapshots = list(db.scalars(
        select(StaffContributionSnapshot)
        .order_by(desc(StaffContributionSnapshot.completed_at))
    ).all())
    if current_user.role == UserRole.staff:
        snapshots = [
            snapshot
            for snapshot in snapshots
            if current_user.id in (snapshot.contributor_ids or [])
        ]
    snapshots = snapshots[skip : skip + limit]

    return [
        {
            "id": snapshot.id,
            "taskId": snapshot.task_id,
            "bookingId": snapshot.booking_id,
            "projectName": snapshot.project_name,
            "taskTitle": snapshot.task_title,
            "contributorIds": snapshot.contributor_ids or [],
            "contributorEmails": snapshot.contributor_emails or [],
            "completedAt": snapshot.completed_at,
        }
        for snapshot in snapshots
    ]
