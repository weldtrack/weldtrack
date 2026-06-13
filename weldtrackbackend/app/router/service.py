from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.db import get_db
from app.models.service import Service
from app.schemas.service import (
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
)

router = APIRouter(prefix="/api/services", tags=["services"])


@router.get("", response_model=list[ServiceResponse])
def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Get all services"""
    query = select(Service).offset(skip).limit(limit)
    services = db.scalars(query).all()
    return services


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific service"""
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    payload: ServiceCreate,
    db: Session = Depends(get_db),
):
    """Create a new service"""
    # Check if service with same name already exists
    existing = db.scalars(select(Service).where(Service.name == payload.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Service with this name already exists",
        )
    
    service = Service(**payload.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    payload: ServiceUpdate,
    db: Session = Depends(get_db),
):
    """Update a service"""
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    
    # Check if new name conflicts with existing service
    if payload.name and payload.name != service.name:
        existing = db.scalars(select(Service).where(Service.name == payload.name)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Service with this name already exists",
            )
    
    for key, value in payload.model_dump(exclude_unset=True).items():
        if hasattr(service, key):
            setattr(service, key, value)
    
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
):
    """Delete a service"""
    service = db.get(Service, service_id)
    if not service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    
    db.delete(service)
    db.commit()
