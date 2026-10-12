from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.auth.domain.entities.device import Device


class DeviceRepository(Protocol):
    async def get_by_id(self, device_id: UUID) -> Device | None:
        ...

    async def get_by_user_and_client_id(
        self,
        user_id: UUID,
        client_device_id: str,
    ) -> Device | None:
        ...

    async def list_by_user(self, user_id: UUID) -> list[Device]:
        ...

    async def save(self, device: Device) -> None:
        ...
