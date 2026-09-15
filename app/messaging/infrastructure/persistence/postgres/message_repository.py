from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.domain.entities.message import Message
from app.messaging.domain.exceptions import DomainError
from app.messaging.infrastructure.persistence.postgres.mappers.message_mapper import (
    to_domain,
    to_model,
)
from app.messaging.infrastructure.persistence.postgres.models.message import MessageModel


class MessageAlreadyExistsError(DomainError):
    """Raised when client_message_id or sequence uniqueness is violated."""


class PostgresMessageRepository:
    """Postgres-backed message repository using SQLAlchemy ORM."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_latest_by_conversation_ids(
        self,
        conversation_ids: list[UUID],
    ) -> dict[UUID, Message]:
        if not conversation_ids:
            return {}

        # PostgreSQL DISTINCT ON: latest sequence per conversation.
        stmt = (
            select(MessageModel)
            .where(MessageModel.conversation_id.in_(conversation_ids))
            .distinct(MessageModel.conversation_id)
            .order_by(
                MessageModel.conversation_id,
                MessageModel.sequence.desc(),
            )
        )
        result = await self._session.execute(stmt)
        return {
            model.conversation_id: to_domain(model)
            for model in result.scalars().all()
        }

    async def save(self, message: Message) -> None:
        self._session.add(to_model(message))
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise MessageAlreadyExistsError(
                "Message already exists for this client_message_id or sequence"
            ) from exc
