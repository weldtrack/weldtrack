from pathlib import PurePosixPath
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import RedirectResponse

from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole
from app.services import object_storage

router = APIRouter(prefix="/uploads", tags=["uploads"])

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}
MAX_FILE_SIZE = 5 * 1024 * 1024
ALLOWED_FOLDERS = {"avatars", "services", "jobs"}


async def store_image(file: UploadFile, folder: str) -> str:
    extension = ALLOWED_IMAGE_TYPES.get(file.content_type or "")
    if extension is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image format. Allowed: JPEG, PNG, WebP, GIF.",
        )
    content = await file.read()
    if not content or len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image must be non-empty and no larger than 5MB.",
        )
    object_name = f"{folder}/{uuid4().hex}.{extension}"
    object_storage.upload(object_name, content, file.content_type or "application/octet-stream")
    return object_storage.public_url(object_name)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    folder: str = Query("jobs"),
    current_user: User = Depends(get_current_user),
):
    if folder not in ALLOWED_FOLDERS:
        raise HTTPException(status_code=400, detail="Invalid image folder")
    if folder == "services" and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Only admins can upload service images")
    if folder == "jobs" and current_user.role not in {UserRole.admin, UserRole.staff}:
        raise HTTPException(status_code=403, detail="Only staff and admins can upload job images")
    return {"url": await store_image(file, folder)}


@router.get("/{object_path:path}")
def get_image(object_path: str):
    clean_path = str(PurePosixPath(object_path))
    if clean_path.startswith("../") or clean_path == ".":
        raise HTTPException(status_code=400, detail="Invalid object path")
    return RedirectResponse(object_storage.public_url(clean_path))
