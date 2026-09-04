from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.domain.entities.user import User
from app.auth.domain.exceptions import UserAlreadyExistsError
from app.auth.infrastructure.persistence.postgres.mappers.user_mapper import (
    apply_domain,
    to_domain,
    to_model,
)
from app.auth.infrastructure.persistence.postgres.models.user import UserModel


class PostgresUserRepository:
    """Postgres-backed user repository using SQLAlchemy ORM."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(
            UserModel.email == email.strip().lower(),
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_domain(model) if model is not None else None

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return to_domain(model) if model is not None else None

    async def save(self, user: User) -> None:
        model = await self._session.get(UserModel, user.id)
        if model is None:
            self._session.add(to_model(user))
        else:
            apply_domain(model, user)

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise UserAlreadyExistsError(
                f"User with email {user.email.value} already exists"
            ) from exc

    async def delete(self, user_id: UUID) -> None:
        model = await self._session.get(UserModel, user_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()
