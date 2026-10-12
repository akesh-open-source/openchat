from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class CreateProfileRequest(BaseModel):
    user_id: UUID
    display_name: str = Field(min_length=3, max_length=30)
    email: EmailStr | None = None


class CreateProfileResponse(BaseModel):
    user_id: UUID
    display_name: str
    email: EmailStr | None = None
    created: bool
    created_at: datetime
    updated_at: datetime
