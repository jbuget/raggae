from uuid import UUID

from raggae.application.dto.agent_configuration_dto import AgentConfigurationDTO
from raggae.application.interfaces.repositories.agent_configuration_repository import (
    AgentConfigurationRepository,
)
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.exceptions.user_exceptions import UserNotFoundError
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType


class GetUserAgentConfiguration:
    """Use Case: Get the agent configuration for a user."""

    def __init__(
        self,
        user_repository: UserRepository,
        agent_configuration_repository: AgentConfigurationRepository,
    ) -> None:
        self._user_repository = user_repository
        self._agent_configuration_repository = agent_configuration_repository

    async def execute(self, user_id: UUID) -> AgentConfigurationDTO | None:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        config = await self._agent_configuration_repository.find_by_owner(
            user_id, AgentConfigurationType.USER
        )
        if config is None:
            return None
        return AgentConfigurationDTO.from_entity(config)
