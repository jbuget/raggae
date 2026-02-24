from typing import Protocol
from uuid import UUID

from raggae.domain.entities.organization_invitation import OrganizationInvitation


class OrganizationInvitationRepository(Protocol):
    """Interface for organization invitation persistence."""

    async def save(self, invitation: OrganizationInvitation) -> None: ...

    async def find_by_id(self, invitation_id: UUID) -> OrganizationInvitation | None: ...

    async def find_by_token_hash(self, token_hash: str) -> OrganizationInvitation | None: ...

    async def find_pending_by_organization_and_email(
        self, organization_id: UUID, email: str
    ) -> OrganizationInvitation | None: ...

    async def find_by_organization_id(self, organization_id: UUID) -> list[OrganizationInvitation]: ...
