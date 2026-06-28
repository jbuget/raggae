from typing import Protocol
from uuid import UUID

from raggae.domain.entities.project_mcp_activation import ProjectMcpActivation


class ProjectMcpActivationRepository(Protocol):
    """Interface for project ↔ MCP server activation persistence."""

    async def save(self, activation: ProjectMcpActivation) -> None:
        """Insert or update an activation by (project_id, org_mcp_server_id)."""
        ...

    async def find(self, project_id: UUID, org_mcp_server_id: UUID) -> ProjectMcpActivation | None: ...

    async def list_by_project_id(self, project_id: UUID) -> list[ProjectMcpActivation]: ...

    async def list_by_org_mcp_server_id(self, org_mcp_server_id: UUID) -> list[ProjectMcpActivation]: ...

    async def delete(self, project_id: UUID, org_mcp_server_id: UUID) -> None: ...

    async def delete_by_org_mcp_server_id(self, org_mcp_server_id: UUID) -> None:
        """Delete all activations for a given MCP server (cascade on server removal)."""
        ...

    async def count_active_activations(self) -> int:
        """Count all project activations marked `is_active=true` across the platform."""
        ...

    async def count_distinct_active_projects(self) -> int:
        """Count distinct projects with at least one `is_active=true` activation."""
        ...
