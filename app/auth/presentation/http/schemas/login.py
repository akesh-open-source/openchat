from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    device_id: str = Field(min_length=1, max_length=128)
    device_name: str | None = Field(default=None, max_length=120)


class LoginUserResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class DeviceResponse(BaseModel):
    id: UUID
    client_device_id: str
    name: str | None
    user_agent: str | None
    created_at: datetime
    last_seen_at: datetime


class SessionResponse(BaseModel):
    id: UUID
    device_id: UUID
    ip_address: str | None
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
