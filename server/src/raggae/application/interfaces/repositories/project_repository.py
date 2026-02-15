from typing import Protocol
from uuid import UUID

from raggae.domain.entities.project import Project


class ProjectRepository(Protocol):
    """Interface for project persistence."""

    async def save(self, project: Project) -> None: ...

    async def find_by_id(self, project_id: UUID) -> Project | None: ...

    async def find_by_user_id(self, user_id: UUID) -> list[Project]: ...

    async def delete(self, project_id: UUID) -> None: ...
