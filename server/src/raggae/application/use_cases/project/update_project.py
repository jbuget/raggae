from dataclasses import replace
from uuid import UUID

from raggae.application.constants import MAX_PROJECT_SYSTEM_PROMPT_LENGTH
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.domain.exceptions.project_exceptions import (
    ProjectNotFoundError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


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
        chunking_strategy: ChunkingStrategy | None = None,
        parent_child_chunking: bool | None = None,
    ) -> ProjectDTO:
        if len(system_prompt) > MAX_PROJECT_SYSTEM_PROMPT_LENGTH:
            raise ProjectSystemPromptTooLongError(
                f"System prompt exceeds {MAX_PROJECT_SYSTEM_PROMPT_LENGTH} characters"
            )
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        updated_project = replace(
            project,
            name=name,
            description=description,
            system_prompt=system_prompt,
            chunking_strategy=project.chunking_strategy
            if chunking_strategy is None
            else chunking_strategy,
            parent_child_chunking=project.parent_child_chunking
            if parent_child_chunking is None
            else parent_child_chunking,
        )
        await self._project_repository.save(updated_project)
        return ProjectDTO.from_entity(updated_project)
