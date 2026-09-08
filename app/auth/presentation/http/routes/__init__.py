from fastapi import APIRouter

from app.auth.presentation.http.routes.login import router as login_router
from app.auth.presentation.http.routes.register import router as register_router

router = APIRouter()
router.include_router(register_router)
router.include_router(login_router)

__all__ = ["router"]
