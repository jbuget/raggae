from uuid import UUID

from raggae.domain.entities.agent_configuration import SYSTEM_OWNER_ID, AgentConfiguration
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType


class InMemoryAgentConfigurationRepository:
    """In-memory agent configuration repository for testing."""

    def __init__(self) -> None:
        self._store: dict[tuple[UUID, AgentConfigurationType], AgentConfiguration] = {}

    async def find_by_owner(
        self, owner_id: UUID, owner_type: AgentConfigurationType
    ) -> AgentConfiguration | None:
        return self._store.get((owner_id, owner_type))

    async def find_app_defaults(self) -> AgentConfiguration | None:
        return self._store.get((SYSTEM_OWNER_ID, AgentConfigurationType.APP))

    async def save(self, config: AgentConfiguration) -> None:
        self._store[(config.owner_id, config.type)] = config

    async def delete_by_owner(self, owner_id: UUID, owner_type: AgentConfigurationType) -> None:
        self._store.pop((owner_id, owner_type), None)
