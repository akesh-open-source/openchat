from __future__ import annotations

from app.auth.domain.entities.user import User
from app.auth.domain.value_objects.display_name import DisplayName
from app.auth.domain.value_objects.email import Email
from app.auth.domain.value_objects.password import Password
from app.auth.infrastructure.persistence.postgres.models.user import UserModel


def to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=Email(model.email),
        display_name=DisplayName(model.display_name),
        password=Password(model.password_hash),
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        email=user.email.value,
        display_name=user.display_name.value,
        password_hash=user.password.hashed_value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def apply_domain(model: UserModel, user: User) -> None:
    model.email = user.email.value
    model.display_name = user.display_name.value
    model.password_hash = user.password.hashed_value
    model.is_active = user.is_active
    model.updated_at = user.updated_at
