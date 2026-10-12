from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.entities.device import Device
from app.auth.infrastructure.persistence.postgres.mappers.device_mapper import (
    apply_domain,
    to_domain,
    to_model,
)
from app.auth.infrastructure.persistence.postgres.models.device import DeviceModel


class PostgresDeviceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, device_id: UUID) -> Device | None:
        model = await self._session.get(DeviceModel, device_id)
        return to_domain(model) if model is not None else None

    async def get_by_user_and_client_id(
        self,
        user_id: UUID,
        client_device_id: str,
    ) -> Device | None:
        stmt = select(DeviceModel).where(
            DeviceModel.user_id == user_id,
            DeviceModel.client_device_id == client_device_id.strip(),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def list_by_user(self, user_id: UUID) -> list[Device]:
        stmt = (
            select(DeviceModel)
            .where(DeviceModel.user_id == user_id)
            .order_by(DeviceModel.last_seen_at.desc())
        )
        result = await self._session.execute(stmt)
        return [to_domain(m) for m in result.scalars().all()]

    async def save(self, device: Device) -> None:
        model = await self._session.get(DeviceModel, device.id)
        if model is None:
            self._session.add(to_model(device))
        else:
            apply_domain(model, device)
        await self._session.flush()
