from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Literal


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    pricing_type: Literal["hourly", "fixed", "hybrid"] = "hourly"
    price_fixed: float = Field(default=0.0, ge=0.0)
    price_hour: float = Field(default=0.0, ge=0.0)
    image_url: Optional[str] = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pricing_type: Optional[Literal["hourly", "fixed", "hybrid"]] = None
    price_fixed: Optional[float] = Field(default=None, ge=0.0)
    price_hour: Optional[float] = Field(default=None, ge=0.0)
    image_url: Optional[str] = None


class ServiceResponse(ServiceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
