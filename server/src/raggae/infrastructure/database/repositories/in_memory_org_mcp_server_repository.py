from uuid import UUID

from raggae.domain.entities.org_mcp_server import OrgMcpServer


class InMemoryOrgMcpServerRepository:
    """In-memory MCP server repository for tests and dev mode."""

    def __init__(self) -> None:
        self._servers: dict[UUID, OrgMcpServer] = {}

    async def save(self, server: OrgMcpServer) -> None:
        self._servers[server.id] = server

    async def find_by_id(self, server_id: UUID, organization_id: UUID) -> OrgMcpServer | None:
        server = self._servers.get(server_id)
        if server is None or server.organization_id != organization_id:
            return None
        return server

    async def find_by_slug(self, organization_id: UUID, slug: str) -> OrgMcpServer | None:
        for server in self._servers.values():
            if server.organization_id == organization_id and server.slug == slug:
                return server
        return None

    async def list_by_org_id(self, organization_id: UUID) -> list[OrgMcpServer]:
        return [s for s in self._servers.values() if s.organization_id == organization_id]

    async def delete(self, server_id: UUID, organization_id: UUID) -> None:
        server = self._servers.get(server_id)
        if server is None or server.organization_id != organization_id:
            return
        del self._servers[server_id]

    async def count_all(self) -> int:
        return len(self._servers)

    async def count_active(self) -> int:
        return sum(1 for s in self._servers.values() if s.is_active)
