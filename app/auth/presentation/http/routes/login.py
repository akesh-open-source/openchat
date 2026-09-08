from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.application.commands.login_user import LoginUserCommand
from app.auth.application.services.login_service import LoginService
from app.auth.presentation.http.dependencies import get_login_service
from app.auth.presentation.http.schemas import LoginUserRequest, LoginUserResponse

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/login",
    response_model=LoginUserResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginUserRequest,
    service: LoginService = Depends(get_login_service),
) -> LoginUserResponse:
    tokens = await service.login(
        LoginUserCommand(
            email=request.email,
            password=request.password,
        )
    )

    return LoginUserResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )
