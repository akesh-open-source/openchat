from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status

from app.auth.application.commands.reset_password import ResetPasswordCommand
from app.auth.application.services.reset_password_service import ResetPasswordService
from app.auth.presentation.http.dependencies import get_reset_password_service
from app.auth.presentation.http.rate_limit import limit_password_reset
from app.auth.presentation.http.schemas import ResetPasswordRequest

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[limit_password_reset()],
)
async def reset_password(
    request: ResetPasswordRequest,
    service: ResetPasswordService = Depends(get_reset_password_service),
) -> Response:
    await service.reset_password(
        ResetPasswordCommand(
            token=request.token,
            new_password=request.new_password,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
