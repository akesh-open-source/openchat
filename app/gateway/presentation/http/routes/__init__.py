from fastapi import APIRouter

from app.gateway.presentation.http.routes.health import router as health_router
from app.gateway.presentation.http.routes.proxy import router as proxy_router

router = APIRouter()
router.include_router(health_router)
router.include_router(proxy_router)

__all__ = ["router"]
