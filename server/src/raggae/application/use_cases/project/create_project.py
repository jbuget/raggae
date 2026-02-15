from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.project_repository import (
    ProjectRepository,
)
from raggae.domain.entities.project import Project


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
    ) -> ProjectDTO:
        project = Project(
            id=uuid4(),
            user_id=user_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            is_published=False,
            created_at=datetime.now(UTC),
        )

        await self._project_repository.save(project)

        return ProjectDTO.from_entity(project)
