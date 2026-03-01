from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.exceptions.organization_exceptions import LastOrganizationOwnerError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


@dataclass(frozen=True)
class Organization:
    """Organization aggregate root."""

    id: UUID
    name: str
    slug: str | None
    description: str | None
    logo_url: str | None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    def update_profile(
        self,
        name: str,
        slug: str | None,
        description: str | None,
        logo_url: str | None,
        updated_at: datetime,
    ) -> "Organization":
        """Return a new organization with updated public profile fields."""
        return replace(
            self,
            name=name,
            slug=slug,
            description=description,
            logo_url=logo_url,
            updated_at=updated_at,
        )

    @staticmethod
    def count_owners(members: list[OrganizationMember]) -> int:
        """Count owner members in a membership list."""
        return sum(1 for member in members if member.role == OrganizationMemberRole.OWNER)

    @staticmethod
    def ensure_can_remove_member(
        target_member: OrganizationMember, members: list[OrganizationMember]
    ) -> None:
        """Raise when removing this member would leave the org without owner."""
        if target_member.role != OrganizationMemberRole.OWNER:
            return
        if Organization.count_owners(members) <= 1:
            raise LastOrganizationOwnerError("Cannot remove the last owner of the organization")

    @staticmethod
    def ensure_can_change_role(
        target_member: OrganizationMember,
        next_role: OrganizationMemberRole,
        members: list[OrganizationMember],
    ) -> None:
        """Raise when changing this role would leave the org without owner."""
        if target_member.role != OrganizationMemberRole.OWNER:
            return
        if next_role == OrganizationMemberRole.OWNER:
            return
        if Organization.count_owners(members) <= 1:
            raise LastOrganizationOwnerError("Cannot demote the last owner of the organization")

    @staticmethod
    def ensure_can_leave(
        leaving_member: OrganizationMember, members: list[OrganizationMember]
    ) -> None:
        """Raise when leaving would leave the organization without owner."""
        Organization.ensure_can_remove_member(target_member=leaving_member, members=members)
