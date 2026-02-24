from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.organization_invitation import OrganizationInvitation
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


@dataclass(frozen=True)
class UserPendingOrganizationInvitationDTO:
    """Pending organization invitation visible in the current user's inbox."""

    id: UUID
    organization_id: UUID
    organization_name: str
    email: str
    role: OrganizationMemberRole
    invited_by_user_id: UUID
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(
        cls,
        invitation: OrganizationInvitation,
        organization_name: str,
    ) -> "UserPendingOrganizationInvitationDTO":
        return cls(
            id=invitation.id,
            organization_id=invitation.organization_id,
            organization_name=organization_name,
            email=invitation.email,
            role=invitation.role,
            invited_by_user_id=invitation.invited_by_user_id,
            expires_at=invitation.expires_at,
            created_at=invitation.created_at,
            updated_at=invitation.updated_at,
        )
