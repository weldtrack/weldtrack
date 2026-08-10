from datetime import datetime, date
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal


class TaskLocationIn(BaseModel):
    province: str
    municipality: str
    barangay: str
    house: str


class TaskCreate(BaseModel):
    bookingId: str | None = None
    projectName: str
    title: str
    description: str | None = ""
    assignedStaffIds: list[str] = Field(min_length=1)
    dueDate: date
    location: TaskLocationIn | None = None


class TaskStatusUpdate(BaseModel):
    status: Literal["pending", "in-progress", "done"]


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    bookingId: str | None
    projectName: str
    title: str
    description: str | None
    assignedStaffIds: list[str]
    assignedStaffEmails: list[str]
    assignedAt: datetime
    dueDate: date
    status: Literal["pending", "in-progress", "done"]
    location: dict


class MaterialLineIn(BaseModel):
    itemId: str
    quantity: int = Field(gt=0)


class TaskMaterialsCreate(BaseModel):
    submittedBy: str | None = None
    taskId: str
    movementType: Literal["stock_out"]
    lines: list[MaterialLineIn] = Field(min_length=1)
    laborHours: float = Field(default=0, ge=0)
    beforeImage: str | None = None
    afterImage: str | None = None
