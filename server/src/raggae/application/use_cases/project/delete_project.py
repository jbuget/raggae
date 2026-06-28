from uuid import UUID

from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType


class DeleteProject:
    """Use Case: Delete a project and its associated configuration."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        agent_configuration_repository: AgentConfigurationRepository,
    ) -> None:
        self._project_repository = project_repository
        self._agent_configuration_repository = agent_configuration_repository

    async def execute(self, project_id: UUID, user_id: UUID) -> None:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        # Delete config row first (no FK cascade because owner_id is polymorphic)
        await self._agent_configuration_repository.delete_by_owner(project_id, AgentConfigurationType.PROJECT)
        await self._project_repository.delete(project_id)
