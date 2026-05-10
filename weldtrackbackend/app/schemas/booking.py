from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.booking import BookingStatus, CancelledBy



class MaterialBase(BaseModel):
    item_id:    str
    name:       str
    qty:        int
    unit_price: float
    subtotal:   float
    is_temp:    Optional[bool] = False


class MaterialCreate(MaterialBase):
    pass


class MaterialResponse(MaterialBase):
    id:         int
    booking_id: int

    model_config = ConfigDict(from_attributes=True)



class BookingBase(BaseModel):
    customer_name:  Optional[str]        = None
    project_type:   str
    email:          Optional[EmailStr] = None
    phone:          Optional[str]      = None
    description:    Optional[str]      = None
    preferred_date: Optional[str]      = None
    schedule_date:  Optional[str]      = None
    estimated_cost: Optional[float]    = None
    material_cost:  Optional[float]    = None
    total_price:    Optional[float]    = None
    # location
    country:       Optional[str] = None
    region:        Optional[str] = None
    province:      Optional[str] = None
    municipality:  Optional[str] = None
    barangay:      Optional[str] = None
    house:         Optional[str] = None


class BookingCreate(BookingBase):
    status: BookingStatus = BookingStatus.pending


class BookingUpdate(BaseModel):
    customer_name:   Optional[str]           = None
    project_type:   Optional[str]           = None
    email:          Optional[EmailStr]      = None
    phone:          Optional[str]           = None
    description:    Optional[str]           = None
    preferred_date: Optional[str]           = None
    schedule_date:  Optional[str]           = None
    estimated_cost: Optional[float]         = None
    material_cost:  Optional[float]         = None
    total_price:    Optional[float]         = None
    # location
    country:       Optional[str] = None
    region:        Optional[str] = None
    province:      Optional[str] = None
    municipality:  Optional[str] = None
    barangay:      Optional[str] = None
    house:         Optional[str] = None
    status:         Optional[BookingStatus] = None
    cancel_reason:  Optional[str]           = None
    cancelled_by:   Optional[CancelledBy]   = None
    before_images:  Optional[list[str]]     = None
    after_images:   Optional[list[str]]     = None
    materials:      Optional[list[MaterialCreate]] = None


class BookingResponse(BookingBase):
    id:            int
    status:        BookingStatus
    created_date:  Optional[datetime]     = None
    cancel_reason: Optional[str]          = None
    cancelled_by:  Optional[CancelledBy]  = None
    before_images: Optional[list[str]]    = []
    after_images:  Optional[list[str]]    = []
    materials:     list[MaterialResponse] = []

    model_config = ConfigDict(from_attributes=True)


class BookingListResponse(BaseModel):
    data:  list[BookingResponse]
    total: int
    page:  int
    size:  int
