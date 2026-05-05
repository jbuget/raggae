from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from raggae.application.dto.user_project_defaults_dto import UserProjectDefaultsDTO


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


class UserProjectDefaultsResponse(BaseModel):
    user_id: UUID
    # Models
    embedding_backend: str | None
    embedding_model: str | None
    embedding_api_key_credential_id: UUID | None
    llm_backend: str | None
    llm_model: str | None
    llm_api_key_credential_id: UUID | None
    # Indexing
    chunking_strategy: str | None
    parent_child_chunking: bool | None
    # Retrieval
    retrieval_strategy: str | None
    retrieval_top_k: int | None
    retrieval_min_score: float | None
    # Reranking
    reranking_enabled: bool | None
    reranker_backend: str | None
    reranker_model: str | None
    reranker_candidate_multiplier: int | None
    # Chat history
    chat_history_window_size: int | None
    chat_history_max_chars: int | None

    @classmethod
    def from_dto(cls, dto: UserProjectDefaultsDTO) -> UserProjectDefaultsResponse:
        return cls.model_validate(dto.__dict__)


class UpsertUserProjectDefaultsRequest(BaseModel):
    # Models
    embedding_backend: str | None = None
    embedding_model: str | None = None
    embedding_api_key_credential_id: UUID | None = None
    llm_backend: str | None = None
    llm_model: str | None = None
    llm_api_key_credential_id: UUID | None = None
    # Indexing
    chunking_strategy: str | None = None
    parent_child_chunking: bool | None = None
    # Retrieval
    retrieval_strategy: str | None = None
    retrieval_top_k: int | None = None
    retrieval_min_score: float | None = None
    # Reranking
    reranking_enabled: bool | None = None
    reranker_backend: str | None = None
    reranker_model: str | None = None
    reranker_candidate_multiplier: int | None = None
    # Chat history
    chat_history_window_size: int | None = None
    chat_history_max_chars: int | None = None
