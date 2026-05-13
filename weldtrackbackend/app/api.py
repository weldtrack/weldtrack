from fastapi import APIRouter

from app.router.user.auth import router as auth_router
from app.router.bookings import router as bookings_router
from app.router.customer_addresses import router as customer_addresses_router
from app.router.feedback import router as feedback_router
from app.router.inventory import router as inventory_router
from app.router.stafftasks import router as stafftasks_router
from app.router.staffcontributions import router as staffcontributions_router
from app.router.attendance import router as attendance_router
from app.router.service import router as service_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(bookings_router)
router.include_router(customer_addresses_router)
router.include_router(feedback_router)
router.include_router(inventory_router)
router.include_router(stafftasks_router)
router.include_router(staffcontributions_router)
router.include_router(attendance_router)
router.include_router(service_router)
