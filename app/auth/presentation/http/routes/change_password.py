from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.auth.application.commands.change_password import ChangePasswordCommand
from app.auth.application.services.change_password_service import ChangePasswordService
from app.auth.presentation.http.dependencies import (
    get_change_password_service,
    get_current_user_id,
)
from app.auth.presentation.http.rate_limit import limit_default
from app.auth.presentation.http.schemas import ChangePasswordRequest

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[limit_default()],
)
async def change_password(
    request: ChangePasswordRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: ChangePasswordService = Depends(get_change_password_service),
) -> Response:
    await service.change_password(
        ChangePasswordCommand(
            user_id=user_id,
            current_password=request.current_password,
            new_password=request.new_password,
        )
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
