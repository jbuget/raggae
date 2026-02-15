from uuid import UUID

from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class GetProject:
    """Use Case: Get a project by ID."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, project_id: UUID, user_id: UUID) -> ProjectDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        return ProjectDTO.from_entity(project)
