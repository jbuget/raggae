from dataclasses import replace
from uuid import UUID

from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class UpdateProject:
    """Use Case: Update a project."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        name: str,
        description: str,
        system_prompt: str,
    ) -> ProjectDTO:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        updated_project = replace(
            project,
            name=name,
            description=description,
            system_prompt=system_prompt,
        )
        await self._project_repository.save(updated_project)
        return ProjectDTO.from_entity(updated_project)
