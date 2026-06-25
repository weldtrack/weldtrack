from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
import shutil
import os
from uuid import uuid4

from app.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate

router = APIRouter(prefix="/profile", tags=["profile"])

# Setup for image storage
UPLOAD_DIR = "uploads/profiles"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

@router.get("/", response_model=UserRead)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/", response_model=UserRead)
def update_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if profile_update.mobile_phone:
        current_user.mobile_phone = profile_update.mobile_phone
    if profile_update.profile_image:
        current_user.profile_image = profile_update.profile_image
    # NOTE: Need to add fullname to User model if required, 
    # but based on requirements I only added profile_image and mobile_phone.
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/upload-image")
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Allowed: jpg, jpeg, png, webp"
        )
    
    # Check file size
    file_data = await file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Max size 5MB"
        )
    
    # Save file
    file_ext = file.filename.split(".")[-1]
    filename = f"{current_user.id}_{uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(file_data)
        
    # Update user model
    current_user.profile_image = f"/static/profiles/{filename}"
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"url": current_user.profile_image}
