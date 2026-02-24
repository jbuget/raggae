from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


@dataclass(frozen=True)
class OrganizationMember:
    """Organization membership entry."""

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: OrganizationMemberRole
    joined_at: datetime

    def with_role(self, role: OrganizationMemberRole) -> "OrganizationMember":
        """Return a new membership with an updated role."""
        return replace(self, role=role)
