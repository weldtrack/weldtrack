from fastapi import APIRouter

from app.router.user.auth import router as auth_router
from app.router.bookings import router as bookings_router
from app.router.feedback import router as feedback_router
from app.router.inventory import router as inventory_router
from app.router.stafftasks import router as stafftasks_router
from app.router.attendance import router as attendance_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(bookings_router)
router.include_router(feedback_router)
router.include_router(inventory_router)
router.include_router(stafftasks_router)
router.include_router(attendance_router)
