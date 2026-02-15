from uuid import UUID

from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)


class ListProjects:
    """Use Case: List all projects for a user."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, user_id: UUID) -> list[ProjectDTO]:
        projects = await self._project_repository.find_by_user_id(user_id)
        return [ProjectDTO.from_entity(p) for p in projects]
