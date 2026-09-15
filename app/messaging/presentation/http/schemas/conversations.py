from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateDirectConversationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    peer_user_id: UUID = Field(..., description="Other participant (auth user id)")


class DirectConversationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    type: str
    peer_user_id: UUID
    created: bool
    created_at: datetime
    updated_at: datetime


class ConversationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    type: str
    peer_user_id: UUID | None
    peer_display_name: str | None = None
    last_message_preview: str | None = None
    last_message_at: datetime | None = None
    last_activity_at: datetime
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[ConversationResponse]
    next_cursor: str | None = None
