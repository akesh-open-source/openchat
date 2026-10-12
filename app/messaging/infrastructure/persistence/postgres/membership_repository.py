from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.domain.entities.membership import Membership
from app.messaging.domain.exceptions import MembershipAlreadyExistsError
from app.messaging.infrastructure.persistence.postgres.mappers.membership_mapper import (
    to_domain,
    to_model,
)
from app.messaging.infrastructure.persistence.postgres.models.membership import (
    MembershipModel,
)


class PostgresMembershipRepository:
    """Postgres-backed membership repository using SQLAlchemy ORM."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(
        self,
        conversation_id: UUID,
        user_id: UUID,
    ) -> Membership | None:
        model = await self._session.get(
            MembershipModel,
            (conversation_id, user_id),
        )
        return to_domain(model) if model is not None else None

    async def list_by_conversation(self, conversation_id: UUID) -> list[Membership]:
        stmt = select(MembershipModel).where(
            MembershipModel.conversation_id == conversation_id,
        )
        result = await self._session.execute(stmt)
        return [to_domain(model) for model in result.scalars().all()]

    async def list_by_user(self, user_id: UUID) -> list[Membership]:
        stmt = select(MembershipModel).where(MembershipModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [to_domain(model) for model in result.scalars().all()]

    async def save(self, membership: Membership) -> None:
        self._session.add(to_model(membership))
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise MembershipAlreadyExistsError(
                f"Membership already exists for user {membership.user_id} "
                f"in conversation {membership.conversation_id}"
            ) from exc

    async def save_many(self, memberships: list[Membership]) -> None:
        for membership in memberships:
            self._session.add(to_model(membership))
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise MembershipAlreadyExistsError(
                "One or more memberships already exist"
            ) from exc
