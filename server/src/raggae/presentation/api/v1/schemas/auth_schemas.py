from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class RegisterUserRequest(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)


class LoginUserRequest(BaseModel):
    email: str
    password: str


class UpdateUserFullNameRequest(BaseModel):
    full_name: str = Field(..., min_length=1)


class UpdateUserLocaleRequest(BaseModel):
    locale: Literal["en", "fr"]


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime
    locale: str = "en"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class OAuthTokenRequest(BaseModel):
    code: str


class OAuthLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False
    account_linked: bool = False
