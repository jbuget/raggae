from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.constants import MAX_PROJECT_SYSTEM_PROMPT_LENGTH
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectSystemPromptTooLongError
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class CreateProject:
    """Use Case: Create a new project."""

    def __init__(self, project_repository: ProjectRepository) -> None:
        self._project_repository = project_repository

    async def execute(
        self,
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
        project = Project(
            id=uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            is_published=False,
            created_at=datetime.now(UTC),
            chunking_strategy=chunking_strategy or ChunkingStrategy.AUTO,
            parent_child_chunking=parent_child_chunking or False,
        )

        await self._project_repository.save(project)

        return ProjectDTO.from_entity(project)
