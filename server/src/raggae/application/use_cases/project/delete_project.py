from uuid import UUID

from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class DeleteProject:
    """Use Case: Delete a project by ID."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(self, project_id: UUID) -> None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        await self._project_repository.delete(project_id)
