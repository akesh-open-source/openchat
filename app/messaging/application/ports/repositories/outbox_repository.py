from __future__ import annotations

from typing import Protocol
from uuid import UUID

from app.messaging.domain.entities.outbox_event import OutboxEvent


class OutboxRepository(Protocol):
    """Port for transactional outbox persistence (no Kafka publish here)."""

    async def save(self, event: OutboxEvent) -> None:
        """Insert an unpublished outbox event."""
        ...

    async def list_by_aggregate_id(self, aggregate_id: UUID) -> list[OutboxEvent]:
        """Return outbox rows for an aggregate (tests / diagnostics)."""
        ...

    async def count(self) -> int:
        """Return total outbox rows (tests)."""
        ...
