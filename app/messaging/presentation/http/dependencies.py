from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.messaging.application.ports.repositories.conversation_repository import (
    ConversationRepository,
)
from app.messaging.application.ports.repositories.membership_repository import (
    MembershipRepository,
)
from app.messaging.infrastructure.persistence.postgres.conversation_repository import (
    PostgresConversationRepository,
)
from app.messaging.infrastructure.persistence.postgres.membership_repository import (
    PostgresMembershipRepository,
)
from app.messaging.infrastructure.persistence.postgres.session import get_session


def get_conversation_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ConversationRepository:
    return PostgresConversationRepository(session)


def get_membership_repository(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MembershipRepository:
    return PostgresMembershipRepository(session)
