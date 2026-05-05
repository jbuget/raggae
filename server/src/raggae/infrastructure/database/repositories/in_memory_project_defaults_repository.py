from uuid import UUID

from raggae.domain.entities.project_defaults import ProjectDefaults
from raggae.domain.value_objects.project_defaults_owner_type import ProjectDefaultsOwnerType


class InMemoryProjectDefaultsRepository:
    """In-memory project defaults repository for testing."""

    def __init__(self) -> None:
        self._store: dict[tuple[UUID, ProjectDefaultsOwnerType], ProjectDefaults] = {}

    async def find_by_owner(
        self, owner_id: UUID, owner_type: ProjectDefaultsOwnerType
    ) -> ProjectDefaults | None:
        return self._store.get((owner_id, owner_type))

    async def save(self, defaults: ProjectDefaults) -> None:
        self._store[(defaults.owner_id, defaults.owner_type)] = defaults
