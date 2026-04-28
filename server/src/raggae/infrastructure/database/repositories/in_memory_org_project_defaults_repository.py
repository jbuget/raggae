from uuid import UUID

from raggae.domain.entities.organization_project_defaults import OrganizationProjectDefaults


class InMemoryOrgProjectDefaultsRepository:
    """In-memory org project defaults repository for testing."""

    def __init__(self) -> None:
        self._store: dict[UUID, OrganizationProjectDefaults] = {}

    async def find_by_organization_id(self, organization_id: UUID) -> OrganizationProjectDefaults | None:
        return self._store.get(organization_id)

    async def save(self, defaults: OrganizationProjectDefaults) -> None:
        self._store[defaults.organization_id] = defaults
