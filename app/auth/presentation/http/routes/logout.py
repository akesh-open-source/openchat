from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.auth.application.commands.logout import LogoutCommand
from app.auth.application.services.logout_service import LogoutService
from app.auth.presentation.http.dependencies import get_logout_service
from app.auth.presentation.http.rate_limit import limit_default
from app.auth.presentation.http.schemas import LogoutRequest

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[limit_default()],
)
async def logout(
    request: LogoutRequest,
    service: LogoutService = Depends(get_logout_service),
) -> Response:
    await service.logout(LogoutCommand(refresh_token=request.refresh_token))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
