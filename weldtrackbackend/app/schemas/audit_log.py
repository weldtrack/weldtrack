from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    id: str
    user_id: str | None = None
    user_name: str | None = None
    user_role: str | None = None
    action: str
    description: str
    auditable_type: str | None = None
    auditable_id: str | None = None
    properties: dict[str, Any] | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    current_page: int
    last_page: int
    per_page: int
    total: int


class AuditStats(BaseModel):
    total_logs: int
    today_logs: int
    actions_count: dict[str, int]


class AuditLogListResponse(BaseModel):
    logs: list[AuditLogResponse]
    pagination: PaginationMeta
    stats: AuditStats
