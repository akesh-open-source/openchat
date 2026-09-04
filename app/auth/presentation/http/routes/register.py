from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.application.commands.register_user import RegisterUserCommand
from app.auth.application.services.registration_service import RegistrationService
from app.auth.presentation.http.dependencies import get_registration_service
from app.auth.presentation.http.schemas import (
    RegisterUserRequest,
    RegisterUserResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/register",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterUserRequest,
    service: RegistrationService = Depends(get_registration_service),
) -> RegisterUserResponse:
    command = RegisterUserCommand(
        email=request.email,
        password=request.password,
        display_name=request.display_name,
    )

    user = await service.register(command)

    return RegisterUserResponse(
        user_id=str(user.id),
        email=user.email.value,
        display_name=user.display_name.value,
    )
