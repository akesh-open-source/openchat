from pydantic import BaseModel, EmailStr, Field


class InitiateRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=3, max_length=30)


class InitiateRegisterResponse(BaseModel):
    detail: str
    # Only populated when AUTH_DEBUG=true — for local testing without email.
    registration_token: str | None = None


class CompleteRegisterRequest(BaseModel):
    token: str = Field(min_length=1)


class CompleteRegisterResponse(BaseModel):
    user_id: str
    email: EmailStr
    display_name: str
