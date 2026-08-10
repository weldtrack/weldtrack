from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class InventoryItemBase(BaseModel):
    name: str
    quantity: int
    unit_price: float
    supplier: Optional[str] = None
    low_stock_threshold: int = 0


class InventoryItemCreate(InventoryItemBase):
    pass


class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None
    supplier: Optional[str] = None
    low_stock_threshold: Optional[int] = None


class InventoryItemResponse(InventoryItemBase):
    id: str
    date_added: datetime

    model_config = ConfigDict(from_attributes=True)


class StockMovementBase(BaseModel):
    item_id: str
    item_name: str
    quantity: int
    type: str  # "stock-in" or "stock-out"
    booking_id: Optional[str] = None
    task_id: Optional[str] = None
    team_emails: list[str] = Field(default_factory=list)


class StockMovementResponse(StockMovementBase):
    id: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
