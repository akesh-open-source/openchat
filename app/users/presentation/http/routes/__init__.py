from fastapi import APIRouter

from app.users.presentation.http.routes.health import router as health_router
from app.users.presentation.http.routes.internal_profiles import (
    router as internal_profiles_router,
)
from app.users.presentation.http.routes.profiles import router as profiles_router

router = APIRouter()
router.include_router(health_router)
router.include_router(internal_profiles_router)
router.include_router(profiles_router)

__all__ = ["router"]
