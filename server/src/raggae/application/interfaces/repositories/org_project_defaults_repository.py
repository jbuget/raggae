from typing import Protocol
from uuid import UUID

from raggae.domain.entities.organization_project_defaults import OrganizationProjectDefaults


class OrgProjectDefaultsRepository(Protocol):
    """Interface for organization project defaults persistence."""

    async def find_by_organization_id(self, organization_id: UUID) -> OrganizationProjectDefaults | None: ...

    async def save(self, defaults: OrganizationProjectDefaults) -> None: ...
