from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SendMessageRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    client_message_id: str = Field(..., min_length=1, max_length=128)
    body: str = Field(..., min_length=1, max_length=10000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    conversation_id: UUID
    sender_id: UUID
    client_message_id: str
    sequence: int
    body: str
    status: str
    created_at: datetime
    created: bool


class MessageListItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    conversation_id: UUID
    sender_id: UUID
    client_message_id: str
    sequence: int
    body: str
    status: str
    created_at: datetime


class MessageListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[MessageListItemResponse]
    next_cursor: str | None = None
