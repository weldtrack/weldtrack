from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class TaskLocationIn(BaseModel):
    province: str
    municipality: str
    barangay: str
    house: str


class TaskCreate(BaseModel):
    bookingId: int | None = None
    projectName: str
    title: str
    description: str | None = ""
    assignedStaffIds: list[int] = Field(min_length=1)
    dueDate: date
    location: TaskLocationIn | None = None


class TaskStatusUpdate(BaseModel):
    status: Literal["pending", "in-progress", "done"]


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    bookingId: int | None
    projectName: str
    title: str
    description: str | None
    assignedStaffIds: list[int]
    assignedStaffEmails: list[str]
    assignedAt: datetime
    dueDate: date
    status: Literal["pending", "in-progress", "done"]
    location: dict


class MaterialLineIn(BaseModel):
    itemId: int
    quantity: int = Field(gt=0)


class TaskMaterialsCreate(BaseModel):
    submittedBy: int | None = None
    taskId: UUID
    movementType: Literal["stock_out"]
    lines: list[MaterialLineIn] = Field(min_length=1)
    laborHours: float = Field(default=0, ge=0)
    beforeImage: str | None = None
    afterImage: str | None = None
