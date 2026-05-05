from typing import Protocol
from uuid import UUID

from raggae.domain.entities.project_defaults import ProjectDefaults
from raggae.domain.value_objects.project_defaults_owner_type import ProjectDefaultsOwnerType


class ProjectDefaultsRepository(Protocol):
    """Interface for project defaults persistence."""

    async def find_by_owner(
        self, owner_id: UUID, owner_type: ProjectDefaultsOwnerType
    ) -> ProjectDefaults | None: ...

    async def save(self, defaults: ProjectDefaults) -> None: ...
