"""Shared test helpers for org_mcp use cases."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.value_objects.mcp_auth_type import McpAuthType


def make_member(role: str) -> object:
    """Build a minimal duck-typed member object with the given role."""
    return type("Member", (), {"role": role})()


def make_server(
    *,
    server_id: UUID | None = None,
    organization_id: UUID | None = None,
    name: str = "Notion",
    slug: str = "notion",
    url: str = "https://mcp.example.com",
    auth_type: McpAuthType = McpAuthType.NONE,
    is_active: bool = True,
    timeout_seconds: int = 30,
) -> OrgMcpServer:
    now = datetime.now(UTC)
    return OrgMcpServer(
        id=server_id or uuid4(),
        organization_id=organization_id or uuid4(),
        name=name,
        slug=slug,
        url=url,
        auth_type=auth_type,
        encrypted_bearer_token="enc" if auth_type == McpAuthType.BEARER else None,
        token_fingerprint="fp" if auth_type == McpAuthType.BEARER else None,
        token_suffix="abcd" if auth_type == McpAuthType.BEARER else None,
        is_active=is_active,
        tools_snapshot=[],
        tools_snapshot_at=now,
        timeout_seconds=timeout_seconds,
        created_at=now,
        updated_at=now,
        created_by_user_id=uuid4(),
    )
