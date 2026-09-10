from fastapi import APIRouter

from app.auth.presentation.http.routes.change_password import (
    router as change_password_router,
)
from app.auth.presentation.http.routes.forgot_password import (
    router as forgot_password_router,
)
from app.auth.presentation.http.routes.login import router as login_router
from app.auth.presentation.http.routes.refresh import router as refresh_router
from app.auth.presentation.http.routes.register import router as register_router
from app.auth.presentation.http.routes.reset_password import (
    router as reset_password_router,
)
from app.auth.presentation.http.routes.sessions import router as sessions_router

router = APIRouter()
router.include_router(register_router)
router.include_router(login_router)
router.include_router(refresh_router)
router.include_router(forgot_password_router)
router.include_router(reset_password_router)
router.include_router(change_password_router)
router.include_router(sessions_router)

__all__ = ["router"]
