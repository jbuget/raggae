from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.constants import MAX_PROJECT_SYSTEM_PROMPT_LENGTH
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.project_exceptions import ProjectSystemPromptTooLongError
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType


class CreateProject:
    """Use Case: Create a new project with a blank configuration (inherits from parent)."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        agent_configuration_repository: AgentConfigurationRepository,
        organization_member_repository: OrganizationMemberRepository | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._agent_configuration_repository = agent_configuration_repository
        self._organization_member_repository = organization_member_repository

    async def execute(
        self,
        user_id: UUID,
        name: str,
        description: str,
        system_prompt: str,
        organization_id: UUID | None = None,
    ) -> ProjectDTO:
        if len(system_prompt) > MAX_PROJECT_SYSTEM_PROMPT_LENGTH:
            raise ProjectSystemPromptTooLongError(
                f"System prompt exceeds {MAX_PROJECT_SYSTEM_PROMPT_LENGTH} characters"
            )

        if organization_id is not None:
            if self._organization_member_repository is None:
                raise OrganizationAccessDeniedError("Organization repository is not configured")
            member = await self._organization_member_repository.find_by_organization_and_user(
                organization_id=organization_id,
                user_id=user_id,
            )
            if member is None:
                raise OrganizationAccessDeniedError("User is not a member of this organization")

        project_id = uuid4()
        project = Project(
            id=project_id,
            user_id=user_id,
            organization_id=organization_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            is_published=False,
            created_at=datetime.now(UTC),
        )
        await self._project_repository.save(project)

        # Create a blank PROJECT config row — all fields null = inherit from parent hierarchy
        project_config = AgentConfiguration(
            id=uuid4(),
            owner_id=project_id,
            owner_type=AgentConfigurationType.PROJECT,
        )
        await self._agent_configuration_repository.save(project_config)

        return ProjectDTO.from_entity(project)
