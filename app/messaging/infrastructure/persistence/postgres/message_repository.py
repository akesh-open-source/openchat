from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.application.dto.message_list_cursor import MessageListCursor
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.entities.message import Message
from app.messaging.domain.entities.outbox_event import OutboxEvent
from app.messaging.domain.exceptions import (
    ConversationNotFoundError,
    MessageAlreadyExistsError,
)
from app.messaging.infrastructure.persistence.postgres.mappers.conversation_mapper import (
    to_domain as conversation_to_domain,
)
from app.messaging.infrastructure.persistence.postgres.mappers.message_mapper import (
    to_domain,
    to_model,
)
from app.messaging.infrastructure.persistence.postgres.mappers.outbox_event_mapper import (
    to_model as outbox_to_model,
)
from app.messaging.infrastructure.persistence.postgres.models.conversation import (
    ConversationModel,
)
from app.messaging.infrastructure.persistence.postgres.models.message import MessageModel


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

    async def get_by_client_message_id(
        self,
        conversation_id: UUID,
        client_message_id: str,
    ) -> Message | None:
        stmt = select(MessageModel).where(
            MessageModel.conversation_id == conversation_id,
            MessageModel.client_message_id == client_message_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def list_by_conversation(
        self,
        conversation_id: UUID,
        *,
        limit: int,
        cursor: MessageListCursor | None = None,
    ) -> list[Message]:
        stmt = select(MessageModel).where(
            MessageModel.conversation_id == conversation_id,
        )
        if cursor is not None:
            stmt = stmt.where(MessageModel.sequence > cursor.sequence)
        stmt = stmt.order_by(MessageModel.sequence.asc()).limit(limit)
        result = await self._session.execute(stmt)
        return [to_domain(model) for model in result.scalars().all()]

    async def create_with_next_sequence(
        self,
        *,
        conversation_id: UUID,
        sender_id: UUID,
        client_message_id: str,
        body: str,
    ) -> Message:
        """FOR UPDATE bump + INSERT in one savepoint (MVP ordering authority)."""
        try:
            async with self._session.begin_nested():
                stmt = (
                    select(ConversationModel)
                    .where(ConversationModel.id == conversation_id)
                    .with_for_update()
                )
                result = await self._session.execute(stmt)
                conversation_model = result.scalar_one_or_none()
                if conversation_model is None:
                    raise ConversationNotFoundError("Conversation not found")

                conversation: Conversation = conversation_to_domain(conversation_model)
                sequence = conversation.allocate_next_sequence()
                conversation_model.next_sequence = conversation.next_sequence

                message = Message.create(
                    conversation_id=conversation_id,
                    sender_id=sender_id,
                    client_message_id=client_message_id,
                    sequence=sequence,
                    body=body,
                )
                # Same nested txn / savepoint as the message (ADR-008).
                # Kafka publish is NOT done here — Phase 3 outbox publisher.
                self._session.add(to_model(message))
                self._session.add(
                    outbox_to_model(OutboxEvent.for_message_created(message))
                )
                await self._session.flush()
                return message
        except IntegrityError as exc:
            raise MessageAlreadyExistsError(
                "Message already exists for this client_message_id or sequence"
            ) from exc

    async def save(self, message: Message) -> None:
        # Nested txn so a unique conflict can be handled without aborting
        # the outer request session (idempotent send path).
        try:
            async with self._session.begin_nested():
                self._session.add(to_model(message))
                await self._session.flush()
        except IntegrityError as exc:
            raise MessageAlreadyExistsError(
                "Message already exists for this client_message_id or sequence"
            ) from exc
