from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.auth.application.services.list_devices_service import ListDevicesService
from app.auth.application.services.list_sessions_service import ListSessionsService
from app.auth.presentation.http.dependencies import (
    get_current_user_id,
    get_list_devices_service,
    get_list_sessions_service,
)
from app.auth.presentation.http.schemas import DeviceResponse, SessionResponse

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
)


@router.get(
    "/devices",
    response_model=list[DeviceResponse],
    status_code=status.HTTP_200_OK,
)
async def list_devices(
    user_id: UUID = Depends(get_current_user_id),
    service: ListDevicesService = Depends(get_list_devices_service),
) -> list[DeviceResponse]:
    devices = await service.list_devices(user_id)
    return [
        DeviceResponse(
            id=device.id,
            client_device_id=device.client_device_id,
            name=device.name,
            user_agent=device.user_agent,
            created_at=device.created_at,
            last_seen_at=device.last_seen_at,
        )
        for device in devices
    ]


@router.get(
    "/sessions",
    response_model=list[SessionResponse],
    status_code=status.HTTP_200_OK,
)
async def list_sessions(
    user_id: UUID = Depends(get_current_user_id),
    service: ListSessionsService = Depends(get_list_sessions_service),
) -> list[SessionResponse]:
    sessions = await service.list_sessions(user_id)
    return [
        SessionResponse(
            id=session.id,
            device_id=session.device_id,
            ip_address=session.ip_address,
            created_at=session.created_at,
            last_seen_at=session.last_seen_at,
            expires_at=session.expires_at,
        )
        for session in sessions
    ]
