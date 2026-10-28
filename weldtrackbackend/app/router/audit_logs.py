from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies.auth import require_admin
from app.schemas.audit_log import AuditLogListResponse
from app.services import audit_service

router = APIRouter(prefix="/admin/audit-logs", tags=["audit-logs"])


@router.get("", response_model=AuditLogListResponse, dependencies=[Depends(require_admin)])
def get_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=5, le=100),
    action: str | None = Query(None),
    role: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    return audit_service.list_audit_logs(
        db,
        page=page,
        per_page=per_page,
        action=action,
        role=role,
        search=search,
    )
