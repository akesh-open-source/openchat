from __future__ import annotations

from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.application.dto.conversation_list_cursor import ConversationListCursor
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.domain.exceptions import ConversationAlreadyExistsError
from app.messaging.domain.value_objects.user_pair import sorted_user_pair
from app.messaging.infrastructure.persistence.postgres.mappers.conversation_mapper import (
    to_domain,
    to_model,
)
from app.messaging.infrastructure.persistence.postgres.models.conversation import (
    ConversationModel,
)
from app.messaging.infrastructure.persistence.postgres.models.membership import (
    MembershipModel,
)


class PostgresConversationRepository:
    """Postgres-backed conversation repository using SQLAlchemy ORM."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, conversation_id: UUID) -> Conversation | None:
        model = await self._session.get(ConversationModel, conversation_id)
        return to_domain(model) if model is not None else None

    async def get_direct_between(
        self,
        user_a_id: UUID,
        user_b_id: UUID,
    ) -> Conversation | None:
        user_a, user_b = sorted_user_pair(user_a_id, user_b_id)
        stmt = select(ConversationModel).where(
            ConversationModel.type == "direct",
            ConversationModel.direct_user_a_id == user_a,
            ConversationModel.direct_user_b_id == user_b,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def list_for_user(
        self,
        user_id: UUID,
        *,
        limit: int,
        cursor: ConversationListCursor | None = None,
    ) -> list[Conversation]:
        stmt = (
            select(ConversationModel)
            .join(
                MembershipModel,
                MembershipModel.conversation_id == ConversationModel.id,
            )
            .where(MembershipModel.user_id == user_id)
            .order_by(
                ConversationModel.updated_at.desc(),
                ConversationModel.id.desc(),
            )
            .limit(limit)
        )
        if cursor is not None:
            stmt = stmt.where(
                or_(
                    ConversationModel.updated_at < cursor.updated_at,
                    and_(
                        ConversationModel.updated_at == cursor.updated_at,
                        ConversationModel.id < cursor.id,
                    ),
                )
            )

        result = await self._session.execute(stmt)
        return [to_domain(model) for model in result.scalars().all()]

    async def save(self, conversation: Conversation) -> None:
        # Nested transaction so a unique-pair conflict can be handled and
        # the outer request transaction can still read the winning row.
        try:
            async with self._session.begin_nested():
                self._session.add(to_model(conversation))
                await self._session.flush()
        except IntegrityError as exc:
            raise ConversationAlreadyExistsError(
                f"Direct conversation already exists for pair "
                f"{conversation.direct_user_a_id}/{conversation.direct_user_b_id}"
            ) from exc
