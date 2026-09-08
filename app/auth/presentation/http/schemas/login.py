from pydantic import BaseModel, EmailStr, Field


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class LoginUserResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
