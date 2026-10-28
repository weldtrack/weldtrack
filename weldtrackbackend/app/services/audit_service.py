from datetime import datetime, timezone
from math import ceil
from typing import Any
from fastapi import Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import (
    AuditLogListResponse,
    AuditLogResponse,
    AuditStats,
    PaginationMeta,
)


def log_action(
    db: Session,
    *,
    action: str,
    description: str,
    user: User | None = None,
    auditable_type: str | None = None,
    auditable_id: str | None = None,
    properties: dict[str, Any] | None = None,
    request: Request | None = None,
) -> AuditLog:
    ip_address = None
    user_agent = None

    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    user_name = user.full_name or user.email if user else "System"
    user_role = user.role.value if (user and hasattr(user.role, "value")) else (str(user.role) if user else "System")

    log_entry = AuditLog(
        user_id=user.id if user else None,
        user_name=user_name,
        user_role=user_role.capitalize(),
        action=action.upper(),
        description=description,
        auditable_type=auditable_type,
        auditable_id=auditable_id,
        properties=properties,
        ip_address=ip_address or "127.0.0.1",
        user_agent=user_agent or "System / API",
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def list_audit_logs(
    db: Session,
    *,
    page: int = 1,
    per_page: int = 20,
    action: str | None = None,
    role: str | None = None,
    search: str | None = None,
) -> AuditLogListResponse:
    safe_page = max(1, page)
    safe_per_page = min(100, max(5, per_page))

    query = select(AuditLog)
    count_query = select(func.count(AuditLog.id))

    if action:
        query = query.where(AuditLog.action == action.upper())
        count_query = count_query.where(AuditLog.action == action.upper())

    if role:
        query = query.where(func.lower(AuditLog.user_role) == role.lower())
        count_query = count_query.where(func.lower(AuditLog.user_role) == role.lower())

    if search:
        pattern = f"%{search}%"
        cond = (
            AuditLog.description.ilike(pattern)
            | AuditLog.user_name.ilike(pattern)
            | AuditLog.action.ilike(pattern)
            | AuditLog.ip_address.ilike(pattern)
        )
        query = query.where(cond)
        count_query = count_query.where(cond)

    total = db.scalar(count_query) or 0
    offset = (safe_page - 1) * safe_per_page

    query = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(safe_per_page)
    logs = list(db.scalars(query).all())

    # Today's activity
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = db.scalar(
        select(func.count(AuditLog.id)).where(AuditLog.created_at >= today_start)
    ) or 0

    # Action counts
    action_counts_query = (
        select(AuditLog.action, func.count(AuditLog.id))
        .group_by(AuditLog.action)
        .order_by(func.count(AuditLog.id).desc())
        .limit(8)
    )
    actions_count = {row[0]: row[1] for row in db.execute(action_counts_query).all()}

    last_page = max(1, ceil(total / safe_per_page))

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        pagination=PaginationMeta(
            current_page=safe_page,
            last_page=last_page,
            per_page=safe_per_page,
            total=total,
        ),
        stats=AuditStats(
            total_logs=total,
            today_logs=today_count,
            actions_count=actions_count,
        ),
    )
