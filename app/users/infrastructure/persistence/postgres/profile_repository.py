from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.users.domain.entities.profile import Profile
from app.users.domain.exceptions import ProfileAlreadyExistsError
from app.users.infrastructure.persistence.postgres.mappers.profile_mapper import (
    apply_domain,
    to_domain,
    to_model,
)
from app.users.infrastructure.persistence.postgres.models.profile import ProfileModel


class PostgresProfileRepository:
    """Postgres-backed profile repository using SQLAlchemy ORM."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        model = await self._session.get(ProfileModel, user_id)
        return to_domain(model) if model is not None else None

    async def get_by_email(self, email: str) -> Profile | None:
        stmt = select(ProfileModel).where(
            ProfileModel.email == email.strip().lower(),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def save(self, profile: Profile) -> None:
        model = await self._session.get(ProfileModel, profile.user_id)
        if model is None:
            self._session.add(to_model(profile))
        else:
            apply_domain(model, profile)

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ProfileAlreadyExistsError(
                f"Profile for user {profile.user_id} already exists"
            ) from exc

    async def delete(self, user_id: UUID) -> None:
        model = await self._session.get(ProfileModel, user_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()
