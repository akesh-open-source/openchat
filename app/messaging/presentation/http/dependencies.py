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
from app.messaging.application.ports.repositories.message_repository import (
    MessageRepository,
)
from app.messaging.application.ports.users_client import UsersClient
from app.messaging.application.services.get_conversation_service import (
    GetConversationService,
)
from app.messaging.application.services.get_or_create_direct_conversation_service import (
    GetOrCreateDirectConversationService,
)
from app.messaging.application.services.list_conversations_service import (
    ListConversationsService,
)
from app.messaging.config.settings import settings
from app.messaging.infrastructure.http.users_client import HttpxUsersClient
from app.messaging.infrastructure.persistence.postgres.conversation_repository import (
    PostgresConversationRepository,
)
from app.messaging.infrastructure.persistence.postgres.membership_repository import (
    PostgresMembershipRepository,
)
from app.messaging.infrastructure.persistence.postgres.message_repository import (
    PostgresMessageRepository,
)
from app.messaging.infrastructure.persistence.postgres.session import get_session
from app.messaging.security.authentication import (
    extract_bearer_token,
    verify_access_token,
)

_users_client = HttpxUsersClient(
    base_url=settings.users_service_url,
    timeout_seconds=settings.users_http_timeout_seconds,
)


def get_conversation_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ConversationRepository:
    return PostgresConversationRepository(session)


def get_membership_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MembershipRepository:
    return PostgresMembershipRepository(session)


def get_message_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MessageRepository:
    return PostgresMessageRepository(session)


def get_users_client() -> UsersClient:
    return _users_client


def get_get_or_create_direct_conversation_service(
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
    membership_repository: Annotated[
        MembershipRepository,
        Depends(get_membership_repository),
    ],
    users_client: Annotated[UsersClient, Depends(get_users_client)],
) -> GetOrCreateDirectConversationService:
    return GetOrCreateDirectConversationService(
        conversation_repository=conversation_repository,
        membership_repository=membership_repository,
        users_client=users_client,
    )


def get_list_conversations_service(
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
    message_repository: Annotated[
        MessageRepository,
        Depends(get_message_repository),
    ],
    users_client: Annotated[UsersClient, Depends(get_users_client)],
) -> ListConversationsService:
    return ListConversationsService(
        conversation_repository=conversation_repository,
        message_repository=message_repository,
        users_client=users_client,
    )


def get_get_conversation_service(
    conversation_repository: Annotated[
        ConversationRepository,
        Depends(get_conversation_repository),
    ],
    membership_repository: Annotated[
        MembershipRepository,
        Depends(get_membership_repository),
    ],
    message_repository: Annotated[
        MessageRepository,
        Depends(get_message_repository),
    ],
    users_client: Annotated[UsersClient, Depends(get_users_client)],
) -> GetConversationService:
    return GetConversationService(
        conversation_repository=conversation_repository,
        membership_repository=membership_repository,
        message_repository=message_repository,
        users_client=users_client,
    )


def get_current_user_id(request: Request) -> UUID:
    """Require a valid Bearer access token; return subject user id."""
    token = extract_bearer_token(request)
    return verify_access_token(token)


def get_access_token(request: Request) -> str:
    """Return the raw Bearer token for forwarding to upstream services."""
    return extract_bearer_token(request)
