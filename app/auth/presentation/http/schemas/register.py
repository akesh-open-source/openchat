from pydantic import BaseModel, EmailStr, Field


class RegisterUserRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=3, max_length=30)


class RegisterUserResponse(BaseModel):
    user_id: str
    email: EmailStr
    display_name: str
