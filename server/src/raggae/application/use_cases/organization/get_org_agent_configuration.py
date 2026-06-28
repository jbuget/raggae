from uuid import UUID

from raggae.application.dto.agent_configuration_dto import AgentConfigurationDTO
from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType


class GetOrgAgentConfiguration:
    """Use Case: Get the agent configuration for an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        agent_configuration_repository: AgentConfigurationRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._agent_configuration_repository = agent_configuration_repository

    async def execute(self, organization_id: UUID, user_id: UUID) -> AgentConfigurationDTO | None:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None:
            raise OrganizationAccessDeniedError(
                f"User {user_id} is not a member of organization {organization_id}"
            )
        config = await self._agent_configuration_repository.find_by_owner(
            organization_id, AgentConfigurationType.ORGA
        )
        if config is None:
            return None
        return AgentConfigurationDTO.from_entity(config)
