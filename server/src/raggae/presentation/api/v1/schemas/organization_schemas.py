from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from raggae.application.dto.org_project_defaults_dto import OrgProjectDefaultsDTO
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class CreateOrganizationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    logo_url: str | None = None


class UpdateOrganizationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    slug: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = None
    logo_url: str | None = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    slug: str | None
    description: str | None
    logo_url: str | None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime


class OrganizationMemberResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    user_first_name: str | None = None
    user_last_name: str | None = None
    user_email: str | None = None
    role: OrganizationMemberRole
    joined_at: datetime


class UpdateOrganizationMemberRoleRequest(BaseModel):
    role: OrganizationMemberRole


class InviteOrganizationMemberRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: OrganizationMemberRole


class OrganizationInvitationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    email: str
    role: OrganizationMemberRole
    status: OrganizationInvitationStatus
    invited_by_user_id: UUID
    expires_at: datetime
    created_at: datetime
    updated_at: datetime
    token_hash: str


class UserPendingOrganizationInvitationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    organization_name: str
    email: str
    role: OrganizationMemberRole
    invited_by_user_id: UUID
    expires_at: datetime
    created_at: datetime
    updated_at: datetime


class AcceptOrganizationInvitationRequest(BaseModel):
    token: str = Field(min_length=8, max_length=255)


class OrganizationProjectDefaultsResponse(BaseModel):
    organization_id: UUID
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
    def from_dto(cls, dto: OrgProjectDefaultsDTO) -> OrganizationProjectDefaultsResponse:
        return cls.model_validate(dto.__dict__)


class UpsertOrganizationProjectDefaultsRequest(BaseModel):
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
