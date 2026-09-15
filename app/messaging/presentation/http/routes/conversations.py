from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.messaging.application.commands.get_conversation import GetConversationQuery
from app.messaging.application.commands.get_or_create_direct_conversation import (
    GetOrCreateDirectConversationCommand,
)
from app.messaging.application.commands.list_conversations import ListConversationsQuery
from app.messaging.application.dto.conversation_summary import ConversationSummary
from app.messaging.application.services.get_conversation_service import (
    GetConversationService,
)
from app.messaging.application.services.get_or_create_direct_conversation_service import (
    GetOrCreateDirectConversationService,
)
from app.messaging.application.services.list_conversations_service import (
    ListConversationsService,
)
from app.messaging.domain.entities.conversation import Conversation
from app.messaging.presentation.http.dependencies import (
    get_access_token,
    get_current_user_id,
    get_get_conversation_service,
    get_get_or_create_direct_conversation_service,
    get_list_conversations_service,
)
from app.messaging.presentation.http.schemas.conversations import (
    ConversationListResponse,
    ConversationResponse,
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


def _to_conversation_response(summary: ConversationSummary) -> ConversationResponse:
    return ConversationResponse(
        id=summary.id,
        type=summary.type.value,
        peer_user_id=summary.peer_user_id,
        peer_display_name=summary.peer_display_name,
        last_activity_at=summary.last_activity_at,
        created_at=summary.created_at,
        updated_at=summary.updated_at,
    )


@router.post(
    "/direct",
    response_model=DirectConversationResponse,
    status_code=status.HTTP_200_OK,
)
async def create_or_get_direct_conversation(
    body: CreateDirectConversationRequest,
    user_id: UUID = Depends(get_current_user_id),
    access_token: str = Depends(get_access_token),
    service: GetOrCreateDirectConversationService = Depends(
        get_get_or_create_direct_conversation_service,
    ),
) -> DirectConversationResponse:
    """Create a 1:1 conversation with peer_user_id, or return the existing one."""
    result = await service.execute(
        GetOrCreateDirectConversationCommand(
            user_id=user_id,
            peer_user_id=body.peer_user_id,
            access_token=access_token,
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


@router.get(
    "",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
)
async def list_conversations(
    user_id: UUID = Depends(get_current_user_id),
    limit: int = Query(default=20, ge=1, le=100),
    cursor: str | None = Query(default=None),
    service: ListConversationsService = Depends(get_list_conversations_service),
) -> ConversationListResponse:
    """List conversations the caller is a member of (newest activity first)."""
    result = await service.execute(
        ListConversationsQuery(user_id=user_id, limit=limit, cursor=cursor),
    )
    return ConversationListResponse(
        items=[_to_conversation_response(item) for item in result.items],
        next_cursor=result.next_cursor,
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
)
async def get_conversation(
    conversation_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: GetConversationService = Depends(get_get_conversation_service),
) -> ConversationResponse:
    """Get one conversation if the caller is a member; otherwise 404."""
    summary = await service.execute(
        GetConversationQuery(user_id=user_id, conversation_id=conversation_id),
    )
    return _to_conversation_response(summary)
