from datetime import UTC, datetime
from uuid import UUID

from raggae.application.dto.org_mcp_server_dto import OrgMcpServerDTO
from raggae.application.interfaces.repositories.org_mcp_server_repository import (
    OrgMcpServerRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.services.mcp_bearer_token_crypto_service import (
    McpBearerTokenCryptoService,
)
from raggae.application.interfaces.services.mcp_client import McpClient
from raggae.application.use_cases.org_mcp._mapping import to_dto
from raggae.domain.exceptions.mcp_exceptions import McpServerNotFoundError
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class RefreshOrgMcpTools:
    """Use case: refresh the tools snapshot of an MCP server by re-calling `tools/list`."""

    def __init__(
        self,
        org_mcp_server_repository: OrgMcpServerRepository,
        organization_member_repository: OrganizationMemberRepository,
        mcp_client: McpClient,
        bearer_token_crypto_service: McpBearerTokenCryptoService,
    ) -> None:
        self._server_repository = org_mcp_server_repository
        self._member_repository = organization_member_repository
        self._mcp_client = mcp_client
        self._crypto = bearer_token_crypto_service

    async def execute(
        self,
        server_id: UUID,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrgMcpServerDTO:
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

        bearer_token = None
        if server.auth_type == McpAuthType.BEARER and server.encrypted_bearer_token is not None:
            bearer_token = self._crypto.decrypt(server.encrypted_bearer_token)

        tools = await self._mcp_client.list_tools(url=server.url, bearer_token=bearer_token)
        refreshed = server.with_refreshed_tools(list(tools), datetime.now(UTC))
        await self._server_repository.save(refreshed)
        return to_dto(refreshed)
