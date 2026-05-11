from dataclasses import replace
from uuid import UUID, uuid4

from raggae.application.constants import MAX_PROJECT_SYSTEM_PROMPT_LENGTH
from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.application.interfaces.repositories.project_snapshot_repository import (
    ProjectSnapshotRepository,
)
from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.services.config_extractor import ConfigExtractor
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.domain.exceptions.project_exceptions import (
    ProjectNotFoundError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class UpdateProject:
    """Use Case: Update a project's name, description, and system prompt."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        organization_member_repository: OrganizationMemberRepository | None = None,
        snapshot_repository: ProjectSnapshotRepository | None = None,
        agent_configuration_repository: AgentConfigurationRepository | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._organization_member_repository = organization_member_repository
        self._snapshot_repository = snapshot_repository
        self._agent_configuration_repository = agent_configuration_repository

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        name: str | None = None,
        description: str | None = None,
        system_prompt: str | None = None,
    ) -> ProjectDTO:
        if system_prompt is not None and len(system_prompt) > MAX_PROJECT_SYSTEM_PROMPT_LENGTH:
            raise ProjectSystemPromptTooLongError(
                f"System prompt exceeds {MAX_PROJECT_SYSTEM_PROMPT_LENGTH} characters"
            )
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if project.user_id != user_id:
            if project.organization_id is None or self._organization_member_repository is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            member = await self._organization_member_repository.find_by_organization_and_user(
                organization_id=project.organization_id,
                user_id=user_id,
            )
            if member is None or member.role not in {
                OrganizationMemberRole.OWNER,
                OrganizationMemberRole.MAKER,
            }:
                raise ProjectNotFoundError(f"Project {project_id} not found")

        updated_project = replace(
            project,
            name=project.name if name is None else name,
            description=project.description if description is None else description,
            system_prompt=project.system_prompt if system_prompt is None else system_prompt,
        )
        await self._project_repository.save(updated_project)

        if self._snapshot_repository is not None:
            # Capture the RESOLVED config for the history, so we know what was actually used
            resolved_config = None
            if self._agent_configuration_repository:
                agent_config = await self._agent_configuration_repository.find_by_owner(
                    owner_id=updated_project.id,
                    owner_type=AgentConfigurationType.PROJECT,
                )
                
                parent_config = None
                if updated_project.organization_id is not None:
                    parent_config = await self._agent_configuration_repository.find_by_owner(
                        updated_project.organization_id, AgentConfigurationType.ORGA
                    )
                else:
                    parent_config = await self._agent_configuration_repository.find_by_owner(
                        user_id, AgentConfigurationType.USER
                    )
                app_config = await self._agent_configuration_repository.find_app_defaults()
                
                # If agent_config is None, we pass an empty one to ConfigExtractor
                # so it can still resolve from parent/app
                base_config = agent_config or AgentConfiguration(
                    id=uuid4(), owner_id=updated_project.id, owner_type=AgentConfigurationType.PROJECT
                )
                resolved_config = ConfigExtractor.resolve(base_config, parent_config, app_config)

            version_number = await self._snapshot_repository.get_next_version_number(updated_project.id)
            snapshot = ProjectSnapshot.from_project(
                project=updated_project,
                version_number=version_number,
                created_by_user_id=user_id,
                agent_config=resolved_config,
            )
            await self._snapshot_repository.save(snapshot)

        return ProjectDTO.from_entity(updated_project)
