from typing import Protocol
from uuid import UUID

from raggae.domain.entities.organization_member import OrganizationMember


class OrganizationMemberRepository(Protocol):
    """Interface for organization membership persistence."""

    async def save(self, member: OrganizationMember) -> None: ...

    async def find_by_id(self, member_id: UUID) -> OrganizationMember | None: ...

    async def find_by_organization_id(self, organization_id: UUID) -> list[OrganizationMember]: ...

    async def find_by_organization_and_user(
        self, organization_id: UUID, user_id: UUID
    ) -> OrganizationMember | None: ...

    async def delete(self, member_id: UUID) -> None: ...
