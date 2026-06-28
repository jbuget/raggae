from typing import Protocol
from uuid import UUID

from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType


class AgentConfigurationRepository(Protocol):
    """Interface for agent configuration persistence."""

    async def find_by_owner(
        self, owner_id: UUID, owner_type: AgentConfigurationType
    ) -> AgentConfiguration | None: ...

    async def find_app_defaults(self) -> AgentConfiguration | None:
        """Return the APP configuration row. Falls back to env vars if absent."""
        ...

    async def save(self, config: AgentConfiguration) -> None: ...

    async def delete_by_owner(self, owner_id: UUID, owner_type: AgentConfigurationType) -> None: ...
