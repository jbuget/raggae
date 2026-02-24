from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.organization_invitation import OrganizationInvitation
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


@dataclass
class OrganizationInvitationDTO:
    """Data Transfer Object for organization invitation."""

    id: UUID
    organization_id: UUID
    email: str
    role: OrganizationMemberRole
    status: OrganizationInvitationStatus
    invited_by_user_id: UUID
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, invitation: OrganizationInvitation) -> "OrganizationInvitationDTO":
        return cls(
            id=invitation.id,
            organization_id=invitation.organization_id,
            email=invitation.email,
            role=invitation.role,
            status=invitation.status,
            invited_by_user_id=invitation.invited_by_user_id,
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
