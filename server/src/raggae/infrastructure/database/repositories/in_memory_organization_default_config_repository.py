from uuid import UUID

from raggae.domain.entities.organization_default_config import OrganizationDefaultConfig


class InMemoryOrganizationDefaultConfigRepository:
    """In-memory organization default config repository for testing."""

    def __init__(self) -> None:
        self._configs: dict[UUID, OrganizationDefaultConfig] = {}

    async def find_by_organization_id(self, organization_id: UUID) -> OrganizationDefaultConfig | None:
        return self._configs.get(organization_id)

    async def save(self, config: OrganizationDefaultConfig) -> None:
        self._configs[config.organization_id] = config
