from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

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


class AcceptOrganizationInvitationRequest(BaseModel):
    token: str = Field(min_length=8, max_length=255)
