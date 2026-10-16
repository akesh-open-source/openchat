from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.domain.entities.outbox_event import OutboxEvent
from app.messaging.infrastructure.persistence.postgres.mappers.outbox_event_mapper import (
    to_domain,
    to_model,
)
from app.messaging.infrastructure.persistence.postgres.models.outbox_event import (
    OutboxEventModel,
)


class PostgresOutboxRepository:
    """Postgres-backed outbox repository (persist only; no Kafka publish)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: OutboxEvent) -> None:
        self._session.add(to_model(event))
        await self._session.flush()

    async def list_by_aggregate_id(self, aggregate_id: UUID) -> list[OutboxEvent]:
        stmt = (
            select(OutboxEventModel)
            .where(OutboxEventModel.aggregate_id == aggregate_id)
            .order_by(OutboxEventModel.created_at.asc())
        )
        result = await self._session.execute(stmt)
        return [to_domain(model) for model in result.scalars().all()]

    async def count(self) -> int:
        result = await self._session.execute(
            select(func.count()).select_from(OutboxEventModel)
        )
        return int(result.scalar_one())
