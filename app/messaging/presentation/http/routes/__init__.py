from fastapi import APIRouter

from app.messaging.presentation.http.routes.conversations import (
    router as conversations_router,
)
from app.messaging.presentation.http.routes.health import router as health_router

router = APIRouter()
router.include_router(health_router)
router.include_router(conversations_router)

__all__ = ["router"]
