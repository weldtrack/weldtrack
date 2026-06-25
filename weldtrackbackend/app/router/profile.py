import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import hash_password
from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.user import UserRead, UserUpdate
from app.services.auth_service import get_user_by_email

router = APIRouter(prefix="/profile", tags=["profile"])

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
    if profile_update.mobile_phone is not None:
        current_user.mobile_phone = profile_update.mobile_phone
    if profile_update.profile_image is not None:
        current_user.profile_image = profile_update.profile_image
    
    if profile_update.email and profile_update.email != current_user.email:
        if current_user.role not in [UserRole.staff, UserRole.admin]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only staff and admins can change email"
            )
        if get_user_by_email(db, profile_update.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered"
            )
        current_user.email = profile_update.email
    
    if profile_update.password:
        current_user.hashed_password = hash_password(profile_update.password)
    
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
    
    # Encode to Base64
    encoded_image = base64.b64encode(file_data).decode('utf-8')
    image_data_uri = f"data:{file.content_type};base64,{encoded_image}"
    
    # Update user model
    current_user.profile_image = image_data_uri
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return {"url": current_user.profile_image}
