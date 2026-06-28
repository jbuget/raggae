from uuid import UUID

from raggae.domain.entities.project_mcp_activation import ProjectMcpActivation


class InMemoryProjectMcpActivationRepository:
    """In-memory project ↔ MCP activation repository for tests and dev mode."""

    def __init__(self) -> None:
        self._activations: dict[tuple[UUID, UUID], ProjectMcpActivation] = {}

    async def save(self, activation: ProjectMcpActivation) -> None:
        self._activations[(activation.project_id, activation.org_mcp_server_id)] = activation

    async def find(self, project_id: UUID, org_mcp_server_id: UUID) -> ProjectMcpActivation | None:
        return self._activations.get((project_id, org_mcp_server_id))

    async def list_by_project_id(self, project_id: UUID) -> list[ProjectMcpActivation]:
        return [a for a in self._activations.values() if a.project_id == project_id]

    async def list_by_org_mcp_server_id(self, org_mcp_server_id: UUID) -> list[ProjectMcpActivation]:
        return [a for a in self._activations.values() if a.org_mcp_server_id == org_mcp_server_id]

    async def delete(self, project_id: UUID, org_mcp_server_id: UUID) -> None:
        self._activations.pop((project_id, org_mcp_server_id), None)

    async def delete_by_org_mcp_server_id(self, org_mcp_server_id: UUID) -> None:
        keys_to_remove = [key for key in self._activations if key[1] == org_mcp_server_id]
        for key in keys_to_remove:
            self._activations.pop(key, None)

    async def count_active_activations(self) -> int:
        return sum(1 for a in self._activations.values() if a.is_active)

    async def count_distinct_active_projects(self) -> int:
        return len({a.project_id for a in self._activations.values() if a.is_active})
