from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerAddressBase(BaseModel):
    label: str
    country: str = "PH"
    region: str = "Bicol Region (Region V)"
    province: str
    municipality: str
    barangay: str
    house: str


class CustomerAddressCreate(CustomerAddressBase):
    is_active: bool = False


class CustomerAddressUpdate(BaseModel):
    label: str | None = None
    country: str | None = None
    region: str | None = None
    province: str | None = None
    municipality: str | None = None
    barangay: str | None = None
    house: str | None = None
    is_active: bool | None = None


class CustomerAddressResponse(CustomerAddressBase):
    id: int
    user_id: int
    is_active: bool
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
