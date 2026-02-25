from uuid import UUID

from raggae.domain.entities.organization_member import OrganizationMember


class InMemoryOrganizationMemberRepository:
    """In-memory organization member repository for testing."""

    def __init__(self) -> None:
        self._members: dict[UUID, OrganizationMember] = {}

    async def save(self, member: OrganizationMember) -> None:
        self._members[member.id] = member

    async def find_by_id(self, member_id: UUID) -> OrganizationMember | None:
        return self._members.get(member_id)

    async def find_by_organization_id(self, organization_id: UUID) -> list[OrganizationMember]:
        return [m for m in self._members.values() if m.organization_id == organization_id]

    async def find_by_user_id(self, user_id: UUID) -> list[OrganizationMember]:
        return [m for m in self._members.values() if m.user_id == user_id]

    async def find_by_organization_and_user(
        self, organization_id: UUID, user_id: UUID
    ) -> OrganizationMember | None:
        for member in self._members.values():
            if member.organization_id == organization_id and member.user_id == user_id:
                return member
        return None

    async def delete(self, member_id: UUID) -> None:
        self._members.pop(member_id, None)
