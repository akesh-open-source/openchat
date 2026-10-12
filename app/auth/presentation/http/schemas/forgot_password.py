from pydantic import BaseModel, EmailStr, Field


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    detail: str
    # Only populated when AUTH_DEBUG=true — for local testing without email.
    reset_token: str | None = None
