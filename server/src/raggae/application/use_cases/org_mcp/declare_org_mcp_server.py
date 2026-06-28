from datetime import UTC, datetime
from uuid import UUID, uuid4

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
from raggae.application.interfaces.services.url_safety_validator import UrlSafetyValidator
from raggae.application.use_cases.org_mcp._mapping import to_dto
from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_slug import slugify
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

MIN_TIMEOUT_SECONDS = 5
MAX_TIMEOUT_SECONDS = 60


class DeclareOrgMcpServer:
    """Use case: declare a new MCP server at organization level."""

    def __init__(
        self,
        org_mcp_server_repository: OrgMcpServerRepository,
        organization_member_repository: OrganizationMemberRepository,
        url_safety_validator: UrlSafetyValidator,
        mcp_client: McpClient,
        bearer_token_crypto_service: McpBearerTokenCryptoService,
    ) -> None:
        self._server_repository = org_mcp_server_repository
        self._member_repository = organization_member_repository
        self._url_safety_validator = url_safety_validator
        self._mcp_client = mcp_client
        self._crypto = bearer_token_crypto_service

    async def execute(
        self,
        organization_id: UUID,
        user_id: UUID,
        name: str,
        url: str,
        auth_type: str,
        bearer_token: str | None,
        timeout_seconds: int,
    ) -> OrgMcpServerDTO:
        await self._ensure_can_manage(organization_id, user_id)
        resolved_auth = McpAuthType(auth_type)
        self._validate_inputs(resolved_auth, bearer_token, timeout_seconds)
        await self._url_safety_validator.validate(url)

        slug = await self._allocate_slug(organization_id, name)
        tools = await self._mcp_client.list_tools(url=url, bearer_token=bearer_token)
        now = datetime.now(UTC)

        if resolved_auth == McpAuthType.BEARER:
            assert bearer_token is not None  # noqa: S101 — guarded by _validate_inputs
            encrypted = self._crypto.encrypt(bearer_token)
            fingerprint = self._crypto.fingerprint(bearer_token)
            suffix = bearer_token[-4:]
        else:
            encrypted = None
            fingerprint = None
            suffix = None

        server = OrgMcpServer(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            slug=slug,
            url=url,
            auth_type=resolved_auth,
            encrypted_bearer_token=encrypted,
            token_fingerprint=fingerprint,
            token_suffix=suffix,
            is_active=True,
            tools_snapshot=list(tools),
            tools_snapshot_at=now,
            timeout_seconds=timeout_seconds,
            created_at=now,
            updated_at=now,
            created_by_user_id=user_id,
        )
        await self._server_repository.save(server)
        return to_dto(server)

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

    @staticmethod
    def _validate_inputs(auth_type: McpAuthType, bearer_token: str | None, timeout_seconds: int) -> None:
        if not MIN_TIMEOUT_SECONDS <= timeout_seconds <= MAX_TIMEOUT_SECONDS:
            raise ValueError(
                f"timeout_seconds must be between {MIN_TIMEOUT_SECONDS} and {MAX_TIMEOUT_SECONDS}"
            )
        if auth_type == McpAuthType.BEARER and not bearer_token:
            raise ValueError("bearer_token is required when auth_type is 'bearer'")

    async def _allocate_slug(self, organization_id: UUID, name: str) -> str:
        base = slugify(name)
        candidate = base
        suffix_index = 2
        while await self._server_repository.find_by_slug(organization_id, candidate) is not None:
            candidate = f"{base}-{suffix_index}"
            suffix_index += 1
        return candidate
