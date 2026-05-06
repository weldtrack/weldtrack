from fastapi import APIRouter

from app.router.user.auth import router as auth_router

router = APIRouter()
router.include_router(auth_router)
