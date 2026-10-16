from __future__ import annotations

from app.messaging.domain.entities.outbox_event import OutboxEvent
from app.messaging.infrastructure.persistence.postgres.models.outbox_event import (
    OutboxEventModel,
)


def to_domain(model: OutboxEventModel) -> OutboxEvent:
    return OutboxEvent(
        id=model.id,
        event_type=model.event_type,
        aggregate_type=model.aggregate_type,
        aggregate_id=model.aggregate_id,
        conversation_id=model.conversation_id,
        payload=dict(model.payload),
        created_at=model.created_at,
        published_at=model.published_at,
    )


def to_model(event: OutboxEvent) -> OutboxEventModel:
    return OutboxEventModel(
        id=event.id,
        event_type=event.event_type,
        aggregate_type=event.aggregate_type,
        aggregate_id=event.aggregate_id,
        conversation_id=event.conversation_id,
        payload=dict(event.payload),
        created_at=event.created_at,
        published_at=event.published_at,
    )
