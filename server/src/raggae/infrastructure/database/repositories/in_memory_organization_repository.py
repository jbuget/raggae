from uuid import UUID

from raggae.domain.entities.organization import Organization


class InMemoryOrganizationRepository:
    """In-memory organization repository for testing."""

    def __init__(self) -> None:
        self._organizations: dict[UUID, Organization] = {}

    async def save(self, organization: Organization) -> None:
        self._organizations[organization.id] = organization

    async def find_by_id(self, organization_id: UUID) -> Organization | None:
        return self._organizations.get(organization_id)

    async def find_by_user_id(self, user_id: UUID) -> list[Organization]:
        return [org for org in self._organizations.values() if org.created_by_user_id == user_id]

    async def find_by_slug(self, slug: str) -> Organization | None:
        for organization in self._organizations.values():
            if organization.slug == slug:
                return organization
        return None

    async def delete(self, organization_id: UUID) -> None:
        self._organizations.pop(organization_id, None)
