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
from raggae.application.interfaces.services.url_safety_validator import UrlSafetyValidator
from raggae.application.use_cases.org_mcp._mapping import to_dto
from raggae.application.use_cases.org_mcp.declare_org_mcp_server import (
    MAX_TIMEOUT_SECONDS,
    MIN_TIMEOUT_SECONDS,
)
from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.exceptions.mcp_exceptions import McpServerNotFoundError
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class UpdateOrgMcpServer:
    """Use case: update editable settings (name/url/timeout/auth) of an MCP server."""

    def __init__(
        self,
        org_mcp_server_repository: OrgMcpServerRepository,
        organization_member_repository: OrganizationMemberRepository,
        url_safety_validator: UrlSafetyValidator,
        bearer_token_crypto_service: McpBearerTokenCryptoService,
    ) -> None:
        self._server_repository = org_mcp_server_repository
        self._member_repository = organization_member_repository
        self._url_safety_validator = url_safety_validator
        self._crypto = bearer_token_crypto_service

    async def execute(
        self,
        server_id: UUID,
        organization_id: UUID,
        user_id: UUID,
        name: str,
        url: str,
        timeout_seconds: int,
        auth_type: str | None,
        bearer_token: str | None,
    ) -> OrgMcpServerDTO:
        await self._ensure_can_manage(organization_id, user_id)
        if not MIN_TIMEOUT_SECONDS <= timeout_seconds <= MAX_TIMEOUT_SECONDS:
            raise ValueError(
                f"timeout_seconds must be between {MIN_TIMEOUT_SECONDS} and {MAX_TIMEOUT_SECONDS}"
            )

        server = await self._server_repository.find_by_id(server_id, organization_id)
        if server is None:
            raise McpServerNotFoundError(f"MCP server {server_id} not found")

        if url != server.url:
            await self._url_safety_validator.validate(url)

        now = datetime.now(UTC)
        updated = server.with_updated_settings(
            name=name,
            url=url,
            timeout_seconds=timeout_seconds,
            updated_at=now,
        )
        updated = self._apply_auth_change(updated, auth_type, bearer_token, now)

        await self._server_repository.save(updated)
        return to_dto(updated)

    def _apply_auth_change(
        self,
        server: OrgMcpServer,
        auth_type: str | None,
        bearer_token: str | None,
        now: datetime,
    ) -> OrgMcpServer:
        if auth_type is None:
            return server
        resolved = McpAuthType(auth_type)
        if resolved == McpAuthType.NONE:
            return server.without_auth(now)
        if not bearer_token:
            raise ValueError("bearer_token is required when auth_type is 'bearer'")
        encrypted = self._crypto.encrypt(bearer_token)
        fingerprint = self._crypto.fingerprint(bearer_token)
        suffix = bearer_token[-4:]
        return server.with_bearer_token(
            encrypted_token=encrypted,
            fingerprint=fingerprint,
            suffix=suffix,
            updated_at=now,
        )

    async def _ensure_can_manage(self, organization_id: UUID, user_id: UUID) -> None:
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
