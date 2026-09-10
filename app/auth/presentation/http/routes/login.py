from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status

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
    http_request: Request,
    service: LoginService = Depends(get_login_service),
) -> LoginUserResponse:
    user_agent = http_request.headers.get("user-agent")
    client = http_request.client
    ip_address = client.host if client is not None else None

    tokens = await service.login(
        LoginUserCommand(
            email=request.email,
            password=request.password,
            device_id=request.device_id,
            device_name=request.device_name,
            user_agent=user_agent,
            ip_address=ip_address,
        )
    )

    return LoginUserResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )
