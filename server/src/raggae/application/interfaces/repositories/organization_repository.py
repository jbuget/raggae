from typing import Protocol
from uuid import UUID

from raggae.domain.entities.organization import Organization


class OrganizationRepository(Protocol):
    """Interface for organization persistence."""

    async def save(self, organization: Organization) -> None: ...

    async def find_by_id(self, organization_id: UUID) -> Organization | None: ...

    async def find_by_user_id(self, user_id: UUID) -> list[Organization]: ...

    async def find_by_slug(self, slug: str) -> Organization | None: ...

    async def delete(self, organization_id: UUID) -> None: ...
