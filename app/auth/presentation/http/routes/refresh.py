from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.application.commands.refresh_tokens import RefreshTokensCommand
from app.auth.application.services.refresh_token_service import RefreshTokenService
from app.auth.presentation.http.dependencies import get_refresh_token_service
from app.auth.presentation.http.rate_limit import limit_refresh
from app.auth.presentation.http.schemas import RefreshTokensRequest, RefreshTokensResponse

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/refresh",
    response_model=RefreshTokensResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[limit_refresh()],
)
async def refresh_tokens(
    request: RefreshTokensRequest,
    service: RefreshTokenService = Depends(get_refresh_token_service),
) -> RefreshTokensResponse:
    tokens = await service.refresh(
        RefreshTokensCommand(refresh_token=request.refresh_token)
    )
    return RefreshTokensResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
    )
