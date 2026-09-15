from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.entities.session import Session
from app.auth.infrastructure.persistence.postgres.mappers.session_mapper import (
    apply_domain,
    to_domain,
    to_model,
)
from app.auth.infrastructure.persistence.postgres.models.session import SessionModel


class PostgresSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, session_id: UUID) -> Session | None:
        model = await self._session.get(SessionModel, session_id)
        return to_domain(model) if model is not None else None

    async def list_active_by_user(self, user_id: UUID) -> list[Session]:
        now = datetime.now(timezone.utc)
        stmt = (
            select(SessionModel)
            .where(
                SessionModel.user_id == user_id,
                SessionModel.revoked_at.is_(None),
                SessionModel.expires_at > now,
            )
            .order_by(SessionModel.last_seen_at.desc())
        )
        result = await self._session.execute(stmt)
        return [to_domain(m) for m in result.scalars().all()]

    async def save(self, session: Session) -> None:
        model = await self._session.get(SessionModel, session.id)
        if model is None:
            self._session.add(to_model(session))
        else:
            apply_domain(model, session)
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: UUID, *, at: datetime) -> None:
        stmt = (
            update(SessionModel)
            .where(
                SessionModel.user_id == user_id,
                SessionModel.revoked_at.is_(None),
            )
            .values(revoked_at=at)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def revoke_by_id(
        self,
        session_id: UUID,
        user_id: UUID,
        *,
        at: datetime,
    ) -> bool:
        stmt = (
            update(SessionModel)
            .where(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id,
                SessionModel.revoked_at.is_(None),
            )
            .values(revoked_at=at)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return (result.rowcount or 0) > 0
