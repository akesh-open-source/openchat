from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.auth.application.commands.complete_register import CompleteRegisterCommand
from app.auth.application.commands.initiate_register import InitiateRegisterCommand
from app.auth.application.services.complete_register_service import CompleteRegisterService
from app.auth.application.services.initiate_register_service import InitiateRegisterService
from app.auth.config.settings import settings
from app.auth.presentation.http.dependencies import (
    get_complete_register_service,
    get_initiate_register_service,
)
from app.auth.presentation.http.schemas import (
    CompleteRegisterRequest,
    CompleteRegisterResponse,
    InitiateRegisterRequest,
    InitiateRegisterResponse,
)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.post(
    "/initiate-register",
    response_model=InitiateRegisterResponse,
    status_code=status.HTTP_200_OK,
)
async def initiate_register(
    request: InitiateRegisterRequest,
    service: InitiateRegisterService = Depends(get_initiate_register_service),
) -> InitiateRegisterResponse:
    result = await service.initiate(
        InitiateRegisterCommand(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
        )
    )
    return InitiateRegisterResponse(
        detail=result.detail,
        registration_token=result.registration_token if settings.debug else None,
    )


@router.post(
    "/complete-register",
    response_model=CompleteRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def complete_register(
    request: CompleteRegisterRequest,
    service: CompleteRegisterService = Depends(get_complete_register_service),
) -> CompleteRegisterResponse:
    user = await service.complete(CompleteRegisterCommand(token=request.token))
    return CompleteRegisterResponse(
        user_id=str(user.id),
        email=user.email.value,
        display_name=user.display_name.value,
    )
