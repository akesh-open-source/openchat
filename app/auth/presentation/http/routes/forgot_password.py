from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.application.commands.forgot_password import ForgotPasswordCommand
from app.auth.application.services.forgot_password_service import ForgotPasswordService
from app.auth.config.settings import settings
from app.auth.presentation.http.dependencies import get_forgot_password_service
from app.auth.presentation.http.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    status_code=status.HTTP_200_OK,
)
async def forgot_password(
    request: ForgotPasswordRequest,
    service: ForgotPasswordService = Depends(get_forgot_password_service),
) -> ForgotPasswordResponse:
    result = await service.forgot_password(
        ForgotPasswordCommand(email=request.email),
    )

    return ForgotPasswordResponse(
        detail=result.detail,
        reset_token=result.reset_token if settings.debug else None,
    )
