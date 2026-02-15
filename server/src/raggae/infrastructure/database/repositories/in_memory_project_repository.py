from uuid import UUID

from raggae.domain.entities.project import Project


class InMemoryProjectRepository:
    """In-memory project repository for testing."""

    def __init__(self) -> None:
        self._projects: dict[UUID, Project] = {}

    async def save(self, project: Project) -> None:
        self._projects[project.id] = project

    async def find_by_id(self, project_id: UUID) -> Project | None:
        return self._projects.get(project_id)

    async def find_by_user_id(self, user_id: UUID) -> list[Project]:
        return [p for p in self._projects.values() if p.user_id == user_id]

    async def delete(self, project_id: UUID) -> None:
        self._projects.pop(project_id, None)
