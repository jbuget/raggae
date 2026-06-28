from datetime import UTC, datetime
from uuid import uuid4

from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot


def _make_server(**overrides: object) -> OrgMcpServer:
    now = datetime.now(UTC)
    defaults: dict[str, object] = {
        "id": uuid4(),
        "organization_id": uuid4(),
        "name": "Notion",
        "slug": "notion",
        "url": "https://mcp.example.com",
        "auth_type": McpAuthType.NONE,
        "encrypted_bearer_token": None,
        "token_fingerprint": None,
        "token_suffix": None,
        "is_active": True,
        "tools_snapshot": [],
        "tools_snapshot_at": now,
        "timeout_seconds": 30,
        "created_at": now,
        "updated_at": now,
        "created_by_user_id": uuid4(),
    }
    defaults.update(overrides)
    return OrgMcpServer(**defaults)  # type: ignore[arg-type]


def test_masked_token_returns_suffix_when_bearer_set() -> None:
    server = _make_server(
        auth_type=McpAuthType.BEARER,
        encrypted_bearer_token="enc",
        token_fingerprint="fp",
        token_suffix="abcd",
    )

    assert server.masked_token == "...abcd"


def test_masked_token_returns_none_when_no_auth() -> None:
    server = _make_server(auth_type=McpAuthType.NONE)

    assert server.masked_token is None


def test_activate_sets_is_active_true() -> None:
    server = _make_server(is_active=False)

    activated = server.activate()

    assert activated.is_active is True
    assert server.is_active is False  # original unchanged


def test_deactivate_sets_is_active_false() -> None:
    server = _make_server(is_active=True)

    deactivated = server.deactivate()

    assert deactivated.is_active is False
    assert server.is_active is True


def test_with_refreshed_tools_updates_snapshot_and_timestamp() -> None:
    server = _make_server()
    tools = [McpToolSnapshot(name="search", description="", input_schema={})]
    refreshed_at = datetime.now(UTC)

    refreshed = server.with_refreshed_tools(tools, refreshed_at)

    assert refreshed.tools_snapshot == tools
    assert refreshed.tools_snapshot_at == refreshed_at


def test_with_updated_settings_changes_mutable_fields() -> None:
    server = _make_server(name="Old", timeout_seconds=30)
    updated_at = datetime.now(UTC)

    updated = server.with_updated_settings(
        name="New name",
        url="https://new.example.com",
        timeout_seconds=15,
        updated_at=updated_at,
    )

    assert updated.name == "New name"
    assert updated.url == "https://new.example.com"
    assert updated.timeout_seconds == 15
    assert updated.updated_at == updated_at
    # immutable fields preserved
    assert updated.id == server.id
    assert updated.slug == server.slug


def test_with_bearer_token_sets_auth_fields() -> None:
    server = _make_server(auth_type=McpAuthType.NONE)
    updated_at = datetime.now(UTC)

    updated = server.with_bearer_token(
        encrypted_token="encrypted-value",
        fingerprint="fp123",
        suffix="wxyz",
        updated_at=updated_at,
    )

    assert updated.auth_type == McpAuthType.BEARER
    assert updated.encrypted_bearer_token == "encrypted-value"
    assert updated.token_fingerprint == "fp123"
    assert updated.token_suffix == "wxyz"
    assert updated.updated_at == updated_at


def test_without_auth_clears_token_fields() -> None:
    server = _make_server(
        auth_type=McpAuthType.BEARER,
        encrypted_bearer_token="enc",
        token_fingerprint="fp",
        token_suffix="abcd",
    )
    updated_at = datetime.now(UTC)

    updated = server.without_auth(updated_at)

    assert updated.auth_type == McpAuthType.NONE
    assert updated.encrypted_bearer_token is None
    assert updated.token_fingerprint is None
    assert updated.token_suffix is None
    assert updated.updated_at == updated_at
