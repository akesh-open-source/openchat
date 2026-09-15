from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.auth.application.ports.repositories.device_repository import DeviceRepository
from app.auth.domain.entities.device import Device


@dataclass(slots=True)
class ListDevicesService:
    device_repository: DeviceRepository

    async def list_devices(self, user_id: UUID) -> list[Device]:
        return await self.device_repository.list_by_user(user_id)
