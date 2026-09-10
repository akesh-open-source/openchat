from __future__ import annotations

from app.auth.domain.entities.refresh_token import RefreshToken
from app.auth.infrastructure.persistence.postgres.models.refresh_token import (
    RefreshTokenModel,
)


def to_domain(model: RefreshTokenModel) -> RefreshToken:
    return RefreshToken(
        id=model.id,
        user_id=model.user_id,
        token_hash=model.token_hash,
        family_id=model.family_id,
        expires_at=model.expires_at,
        created_at=model.created_at,
        session_id=model.session_id,
        revoked_at=model.revoked_at,
        replaced_by_id=model.replaced_by_id,
    )


def to_model(token: RefreshToken) -> RefreshTokenModel:
    return RefreshTokenModel(
        id=token.id,
        user_id=token.user_id,
        session_id=token.session_id,
        token_hash=token.token_hash,
        family_id=token.family_id,
        expires_at=token.expires_at,
        created_at=token.created_at,
        revoked_at=token.revoked_at,
        replaced_by_id=token.replaced_by_id,
    )


def apply_domain(model: RefreshTokenModel, token: RefreshToken) -> None:
    model.user_id = token.user_id
    model.session_id = token.session_id
    model.token_hash = token.token_hash
    model.family_id = token.family_id
    model.expires_at = token.expires_at
    model.revoked_at = token.revoked_at
    model.replaced_by_id = token.replaced_by_id
