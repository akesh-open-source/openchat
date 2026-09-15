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
