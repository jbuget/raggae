from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.services.mcp_tool_executor import McpToolExecutor
from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.exceptions.mcp_exceptions import (
    McpCallTimeoutError,
    McpServerNotFoundError,
)
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_descriptor import McpToolDescriptor


def _make_descriptor(*, has_bearer_token: bool = False) -> McpToolDescriptor:
    return McpToolDescriptor(
        mcp_server_id=uuid4(),
        mcp_server_slug="notion",
        original_name="search",
        prefixed_name="notion__search",
        description="Search",
        input_schema={},
        server_url="https://mcp.example.com/",
        has_bearer_token=has_bearer_token,
        timeout_seconds=15,
    )


def _make_server_with_bearer(server_id) -> OrgMcpServer:
    now = datetime.now(UTC)
    return OrgMcpServer(
        id=server_id,
        organization_id=uuid4(),
        name="Notion",
        slug="notion",
        url="https://mcp.example.com/",
        auth_type=McpAuthType.BEARER,
        encrypted_bearer_token="encrypted-value",
        token_fingerprint="fp",
        token_suffix="abcd",
        is_active=True,
        tools_snapshot=[],
        tools_snapshot_at=now,
        timeout_seconds=15,
        created_at=now,
        updated_at=now,
        created_by_user_id=uuid4(),
    )


def _build_executor(
    *,
    server: OrgMcpServer | None = None,
    call_result: dict | None = None,
    call_raises: Exception | None = None,
    decrypted: str = "decrypted-token",
) -> tuple[McpToolExecutor, dict[str, object]]:
    server_repo = AsyncMock()
    server_repo.find_by_id = AsyncMock(return_value=server)
    mcp_client = AsyncMock()
    if call_raises is not None:
        mcp_client.call_tool = AsyncMock(side_effect=call_raises)
    else:
        mcp_client.call_tool = AsyncMock(return_value=call_result or {"content": []})
    crypto = Mock()
    crypto.decrypt.return_value = decrypted
    executor = McpToolExecutor(
        org_mcp_server_repository=server_repo,
        mcp_client=mcp_client,
        bearer_token_crypto_service=crypto,
    )
    return executor, {"mcp_client": mcp_client, "crypto": crypto, "server_repo": server_repo}


class TestMcpToolExecutor:
    async def test_executes_without_bearer_when_descriptor_says_so(self) -> None:
        # Given
        descriptor = _make_descriptor(has_bearer_token=False)
        executor, deps = _build_executor()

        # When
        result = await executor.execute(
            descriptor=descriptor, arguments={"q": "hello"}, organization_id=uuid4()
        )

        # Then
        assert result == {"content": []}
        deps["mcp_client"].call_tool.assert_awaited_once_with(  # type: ignore[attr-defined]
            url=descriptor.server_url,
            tool=descriptor.original_name,
            arguments={"q": "hello"},
            timeout_seconds=15,
            bearer_token=None,
        )
        deps["crypto"].decrypt.assert_not_called()  # type: ignore[attr-defined]

    async def test_decrypts_and_passes_bearer_token(self) -> None:
        # Given
        descriptor = _make_descriptor(has_bearer_token=True)
        server = _make_server_with_bearer(descriptor.mcp_server_id)
        executor, deps = _build_executor(server=server, decrypted="clear-token")

        # When
        await executor.execute(descriptor=descriptor, arguments={}, organization_id=server.organization_id)

        # Then
        deps["crypto"].decrypt.assert_called_once_with("encrypted-value")  # type: ignore[attr-defined]
        deps["mcp_client"].call_tool.assert_awaited_once()  # type: ignore[attr-defined]
        kwargs = deps["mcp_client"].call_tool.await_args.kwargs  # type: ignore[attr-defined]
        assert kwargs["bearer_token"] == "clear-token"

    async def test_raises_when_server_with_bearer_is_not_found(self) -> None:
        # Given
        descriptor = _make_descriptor(has_bearer_token=True)
        executor, _ = _build_executor(server=None)

        # When / Then
        with pytest.raises(McpServerNotFoundError):
            await executor.execute(descriptor=descriptor, arguments={}, organization_id=uuid4())

    async def test_propagates_call_tool_errors(self) -> None:
        # Given
        descriptor = _make_descriptor(has_bearer_token=False)
        executor, _ = _build_executor(call_raises=McpCallTimeoutError("timeout"))

        # When / Then
        with pytest.raises(McpCallTimeoutError):
            await executor.execute(descriptor=descriptor, arguments={}, organization_id=uuid4())
