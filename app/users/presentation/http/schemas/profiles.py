from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class ProfileResponse(BaseModel):
    user_id: UUID
    display_name: str
    email: EmailStr | None = None
    bio: str | None = None
    avatar_url: str | None = None
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    """Only these fields may be updated; omit a field to leave it unchanged."""

    display_name: str | None = Field(default=None, min_length=3, max_length=30)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=2048)
