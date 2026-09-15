from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.application.ports.repositories.conversation_repository import (
    ConversationRepository,
)
from app.messaging.application.ports.repositories.membership_repository import (
    MembershipRepository,
)
from app.messaging.application.services.get_or_create_direct_conversation_service import (
    GetOrCreateDirectConversationService,
)
from app.messaging.infrastructure.persistence.postgres.conversation_repository import (
    PostgresConversationRepository,
)
from app.messaging.infrastructure.persistence.postgres.membership_repository import (
    PostgresMembershipRepository,
)
from app.messaging.infrastructure.persistence.postgres.session import get_session
from app.messaging.security.authentication import (
    extract_bearer_token,
    verify_access_token,
)


def get_conversation_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ConversationRepository:
    return PostgresConversationRepository(session)


def get_membership_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MembershipRepository:
    return PostgresMembershipRepository(session)


def get_get_or_create_direct_conversation_service(
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
    membership_repository: Annotated[
        MembershipRepository,
        Depends(get_membership_repository),
    ],
) -> GetOrCreateDirectConversationService:
    return GetOrCreateDirectConversationService(
        conversation_repository=conversation_repository,
        membership_repository=membership_repository,
    )


def get_current_user_id(request: Request) -> UUID:
    """Require a valid Bearer access token; return subject user id."""
    token = extract_bearer_token(request)
    return verify_access_token(token)
