from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


@dataclass
class OrganizationMemberDTO:
    """Data Transfer Object for organization member."""

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrganizationMemberRole
    joined_at: datetime

    @classmethod
    def from_entity(cls, member: OrganizationMember) -> "OrganizationMemberDTO":
        return cls(
            id=member.id,
            organization_id=member.organization_id,
            user_id=member.user_id,
            role=member.role,
            joined_at=member.joined_at,
        )
