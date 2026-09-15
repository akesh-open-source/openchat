from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.messaging.application.commands.get_or_create_direct_conversation import (
    GetOrCreateDirectConversationCommand,
)
from app.messaging.application.services.get_or_create_direct_conversation_service import (
    GetOrCreateDirectConversationService,
)
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.presentation.http.dependencies import (
    get_current_user_id,
    get_get_or_create_direct_conversation_service,
)
from app.messaging.presentation.http.schemas.conversations import (
    CreateDirectConversationRequest,
    DirectConversationResponse,
)

router = APIRouter(
    prefix="/conversations",
    tags=["conversations"],
)


def _peer_user_id(conversation: Conversation, caller_id: UUID) -> UUID:
    if conversation.direct_user_a_id == caller_id:
        assert conversation.direct_user_b_id is not None
        return conversation.direct_user_b_id
    assert conversation.direct_user_a_id is not None
    return conversation.direct_user_a_id


@router.post(
    "/direct",
    response_model=DirectConversationResponse,
    status_code=status.HTTP_200_OK,
)
async def create_or_get_direct_conversation(
    body: CreateDirectConversationRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: GetOrCreateDirectConversationService = Depends(
        get_get_or_create_direct_conversation_service,
    ),
) -> DirectConversationResponse:
    """Create a 1:1 conversation with peer_user_id, or return the existing one."""
    result = await service.execute(
        GetOrCreateDirectConversationCommand(
            user_id=user_id,
            peer_user_id=body.peer_user_id,
        )
    )
    conversation = result.conversation
    return DirectConversationResponse(
        id=conversation.id,
        type=conversation.type.value,
        peer_user_id=_peer_user_id(conversation, user_id),
        created=result.created,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )
