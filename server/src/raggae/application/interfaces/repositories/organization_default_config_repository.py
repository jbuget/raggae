from typing import Protocol
from uuid import UUID

from raggae.domain.entities.organization_default_config import OrganizationDefaultConfig


class OrganizationDefaultConfigRepository(Protocol):
    """Interface for organization default config persistence."""

    async def find_by_organization_id(self, organization_id: UUID) -> OrganizationDefaultConfig | None: ...

    async def save(self, config: OrganizationDefaultConfig) -> None: ...
