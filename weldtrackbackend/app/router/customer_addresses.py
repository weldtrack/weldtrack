from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.customer_address import CustomerAddress
from app.models.user import User, UserRole
from app.router.auth import get_current_user
from app.schemas.customer_address import (
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerAddressUpdate,
)

router = APIRouter(prefix="/customer-addresses", tags=["customer-addresses"])


def require_customer(current_user: User) -> User:
    if current_user.role != UserRole.customer:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Customer access required"
        )
    return current_user


def get_owned_address(
    address_id: int, current_user: User, db: Session
) -> CustomerAddress:
    address = db.scalar(
        select(CustomerAddress).where(
            CustomerAddress.id == address_id,
            CustomerAddress.user_id == current_user.id,
        )
    )
    if address is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )
    return address


def deactivate_other_addresses(
    user_id: int, active_address_id: int | None, db: Session
) -> None:
    addresses = db.scalars(
        select(CustomerAddress).where(CustomerAddress.user_id == user_id)
    ).all()
    for address in addresses:
        should_be_active = (
            address.id == active_address_id if active_address_id is not None else False
        )
        if address.is_active != should_be_active:
            address.is_active = should_be_active
            db.add(address)


@router.get("/me", response_model=list[CustomerAddressResponse])
def list_my_addresses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user = require_customer(current_user)
    return db.scalars(
        select(CustomerAddress)
        .where(CustomerAddress.user_id == current_user.id)
        .order_by(CustomerAddress.is_active.desc(), CustomerAddress.id.asc())
    ).all()


@router.post(
    "", response_model=CustomerAddressResponse, status_code=status.HTTP_201_CREATED
)
def create_address(
    payload: CustomerAddressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user = require_customer(current_user)
    has_existing = db.scalar(
        select(CustomerAddress.id).where(CustomerAddress.user_id == current_user.id)
    )
    should_activate = payload.is_active or has_existing is None

    address = CustomerAddress(
        user_id=current_user.id,
        **payload.model_dump(exclude={"is_active"}),
        is_active=should_activate
    )
    db.add(address)
    db.flush()

    if should_activate:
        deactivate_other_addresses(current_user.id, address.id, db)

    db.commit()
    db.refresh(address)
    return address


@router.patch("/{address_id}", response_model=CustomerAddressResponse)
def update_address(
    address_id: int,
    payload: CustomerAddressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user = require_customer(current_user)
    address = get_owned_address(address_id, current_user, db)

    update_data = payload.model_dump(exclude_unset=True)
    should_activate = update_data.pop("is_active", None)

    for key, value in update_data.items():
        setattr(address, key, value)

    if should_activate is True:
        deactivate_other_addresses(current_user.id, address.id, db)
        address.is_active = True
    elif should_activate is False and address.is_active:
        remaining_address = db.scalar(
            select(CustomerAddress)
            .where(
                CustomerAddress.user_id == current_user.id,
                CustomerAddress.id != address.id,
            )
            .order_by(CustomerAddress.id.asc())
        )
        if remaining_address is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one active address is required",
            )
        deactivate_other_addresses(current_user.id, remaining_address.id, db)
        address.is_active = False

    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.post("/{address_id}/activate", response_model=CustomerAddressResponse)
def activate_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user = require_customer(current_user)
    address = get_owned_address(address_id, current_user, db)
    deactivate_other_addresses(current_user.id, address.id, db)
    address.is_active = True
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user = require_customer(current_user)
    address = get_owned_address(address_id, current_user, db)
    was_active = address.is_active

    db.delete(address)
    db.flush()

    if was_active:
        replacement = db.scalar(
            select(CustomerAddress)
            .where(CustomerAddress.user_id == current_user.id)
            .order_by(CustomerAddress.id.asc())
        )
        if replacement is not None:
            deactivate_other_addresses(current_user.id, replacement.id, db)

    db.commit()
