from typing import Protocol
from uuid import UUID

from raggae.domain.entities.org_mcp_server import OrgMcpServer


class OrgMcpServerRepository(Protocol):
    """Interface for organization MCP server persistence."""

    async def save(self, server: OrgMcpServer) -> None:
        """Insert or update an MCP server by id."""
        ...

    async def find_by_id(self, server_id: UUID, organization_id: UUID) -> OrgMcpServer | None: ...

    async def find_by_slug(self, organization_id: UUID, slug: str) -> OrgMcpServer | None: ...

    async def list_by_org_id(self, organization_id: UUID) -> list[OrgMcpServer]: ...

    async def delete(self, server_id: UUID, organization_id: UUID) -> None: ...

    async def count_all(self) -> int:
        """Count all MCP servers across organizations (for platform-level stats)."""
        ...

    async def count_active(self) -> int:
        """Count MCP servers currently `is_active=true` across organizations."""
        ...
