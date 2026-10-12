from __future__ import annotations

from app.auth.domain.entities.session import Session
from app.auth.infrastructure.persistence.postgres.models.session import SessionModel


def to_domain(model: SessionModel) -> Session:
    return Session(
        id=model.id,
        user_id=model.user_id,
        device_id=model.device_id,
        expires_at=model.expires_at,
        created_at=model.created_at,
        last_seen_at=model.last_seen_at,
        ip_address=model.ip_address,
        revoked_at=model.revoked_at,
    )


def to_model(session: Session) -> SessionModel:
    return SessionModel(
        id=session.id,
        user_id=session.user_id,
        device_id=session.device_id,
        ip_address=session.ip_address,
        expires_at=session.expires_at,
        revoked_at=session.revoked_at,
        created_at=session.created_at,
        last_seen_at=session.last_seen_at,
    )


def apply_domain(model: SessionModel, session: Session) -> None:
    model.user_id = session.user_id
    model.device_id = session.device_id
    model.ip_address = session.ip_address
    model.expires_at = session.expires_at
    model.revoked_at = session.revoked_at
    model.last_seen_at = session.last_seen_at
