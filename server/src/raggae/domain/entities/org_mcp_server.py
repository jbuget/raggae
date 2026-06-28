from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot


@dataclass(frozen=True)
class OrgMcpServer:
    """Organization-level MCP server declaration. Immutable."""

    id: UUID
    organization_id: UUID
    name: str
    slug: str
    url: str
    auth_type: McpAuthType
    encrypted_bearer_token: str | None
    token_fingerprint: str | None
    token_suffix: str | None
    is_active: bool
    tools_snapshot_at: datetime
    timeout_seconds: int
    created_at: datetime
    updated_at: datetime
    created_by_user_id: UUID
    tools_snapshot: list[McpToolSnapshot] = field(default_factory=list)

    @property
    def masked_token(self) -> str | None:
        if self.auth_type != McpAuthType.BEARER or self.token_suffix is None:
            return None
        return f"...{self.token_suffix}"

    def activate(self) -> "OrgMcpServer":
        return replace(self, is_active=True)

    def deactivate(self) -> "OrgMcpServer":
        return replace(self, is_active=False)

    def with_refreshed_tools(self, tools: list[McpToolSnapshot], refreshed_at: datetime) -> "OrgMcpServer":
        return replace(self, tools_snapshot=list(tools), tools_snapshot_at=refreshed_at)

    def with_updated_settings(
        self,
        name: str,
        url: str,
        timeout_seconds: int,
        updated_at: datetime,
    ) -> "OrgMcpServer":
        return replace(
            self,
            name=name,
            url=url,
            timeout_seconds=timeout_seconds,
            updated_at=updated_at,
        )

    def with_bearer_token(
        self,
        encrypted_token: str,
        fingerprint: str,
        suffix: str,
        updated_at: datetime,
    ) -> "OrgMcpServer":
        return replace(
            self,
            auth_type=McpAuthType.BEARER,
            encrypted_bearer_token=encrypted_token,
            token_fingerprint=fingerprint,
            token_suffix=suffix,
            updated_at=updated_at,
        )

    def without_auth(self, updated_at: datetime) -> "OrgMcpServer":
        return replace(
            self,
            auth_type=McpAuthType.NONE,
            encrypted_bearer_token=None,
            token_fingerprint=None,
            token_suffix=None,
            updated_at=updated_at,
        )
