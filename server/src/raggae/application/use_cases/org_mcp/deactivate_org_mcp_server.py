from uuid import UUID

from raggae.application.interfaces.repositories.org_mcp_server_repository import (
    OrgMcpServerRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.domain.exceptions.mcp_exceptions import McpServerNotFoundError
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class DeactivateOrgMcpServer:
    """Use case: deactivate an MCP server at the organization level."""

    def __init__(
        self,
        org_mcp_server_repository: OrgMcpServerRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._server_repository = org_mcp_server_repository
        self._member_repository = organization_member_repository

    async def execute(self, server_id: UUID, organization_id: UUID, user_id: UUID) -> None:
        member = await self._member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None or member.role not in {
            OrganizationMemberRole.OWNER,
            OrganizationMemberRole.MAKER,
        }:
            raise OrganizationAccessDeniedError(
                f"User {user_id} cannot manage MCP servers for organization {organization_id}"
            )
        server = await self._server_repository.find_by_id(server_id, organization_id)
        if server is None:
            raise McpServerNotFoundError(f"MCP server {server_id} not found")
        await self._server_repository.save(server.deactivate())
