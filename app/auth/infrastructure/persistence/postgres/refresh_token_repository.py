from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.entities.refresh_token import RefreshToken
from app.auth.infrastructure.persistence.postgres.mappers.refresh_token_mapper import (
    apply_domain,
    to_domain,
    to_model,
)
from app.auth.infrastructure.persistence.postgres.models.refresh_token import (
    RefreshTokenModel,
)


class PostgresRefreshTokenRepository:
    """Postgres-backed refresh-token repository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, token_id: UUID) -> RefreshToken | None:
        model = await self._session.get(RefreshTokenModel, token_id)
        return to_domain(model) if model is not None else None

    async def save(self, token: RefreshToken) -> None:
        model = await self._session.get(RefreshTokenModel, token.id)
        if model is None:
            self._session.add(to_model(token))
        else:
            apply_domain(model, token)
        await self._session.flush()

    async def revoke_family(self, family_id: UUID, *, at: datetime) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.family_id == family_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=at)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def revoke_all_for_user(self, user_id: UUID, *, at: datetime) -> None:
        stmt = (
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=at)
        )
        await self._session.execute(stmt)
        await self._session.flush()
