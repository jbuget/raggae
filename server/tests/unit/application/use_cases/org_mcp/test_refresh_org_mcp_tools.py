from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_mcp.refresh_org_mcp_tools import RefreshOrgMcpTools
from raggae.domain.exceptions.mcp_exceptions import McpHandshakeError, McpServerNotFoundError
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

from ._helpers import make_member, make_server


def _build_use_case(
    *,
    member_role: OrganizationMemberRole | None = OrganizationMemberRole.OWNER,
    existing_server: object | None = None,
    handshake_tools: list[McpToolSnapshot] | None = None,
    handshake_raises: Exception | None = None,
    decrypted_token: str | None = "decrypted-token",
) -> tuple[RefreshOrgMcpTools, dict[str, object]]:
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    server_repo = AsyncMock()
    server_repo.find_by_id = AsyncMock(return_value=existing_server)
    server_repo.save = AsyncMock()
    mcp_client = AsyncMock()
    if handshake_raises is not None:
        mcp_client.list_tools = AsyncMock(side_effect=handshake_raises)
    else:
        mcp_client.list_tools = AsyncMock(return_value=handshake_tools or [])
    from unittest.mock import Mock

    crypto = Mock()
    crypto.decrypt.return_value = decrypted_token
    use_case = RefreshOrgMcpTools(
        org_mcp_server_repository=server_repo,
        organization_member_repository=member_repo,
        mcp_client=mcp_client,
        bearer_token_crypto_service=crypto,
    )
    return use_case, {
        "server_repo": server_repo,
        "mcp_client": mcp_client,
        "crypto": crypto,
    }


class TestRefreshOrgMcpTools:
    async def test_refresh_updates_snapshot(self) -> None:
        # Given
        existing = make_server()
        new_tools = [
            McpToolSnapshot(name="search", description="", input_schema={}),
            McpToolSnapshot(name="create", description="", input_schema={}),
        ]
        use_case, deps = _build_use_case(existing_server=existing, handshake_tools=new_tools)

        # When
        result = await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
        )

        # Then
        assert len(result.tools_snapshot) == 2
        assert result.tools_snapshot[0].name == "search"
        deps["server_repo"].save.assert_awaited_once()  # type: ignore[attr-defined]

    async def test_refresh_passes_decrypted_bearer_to_client(self) -> None:
        # Given
        existing = make_server(auth_type=McpAuthType.BEARER)
        use_case, deps = _build_use_case(existing_server=existing, decrypted_token="clear-token-1234")

        # When
        await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
        )

        # Then
        deps["mcp_client"].list_tools.assert_awaited_once_with(  # type: ignore[attr-defined]
            url=existing.url, bearer_token="clear-token-1234"
        )

    async def test_refresh_no_auth_does_not_call_crypto(self) -> None:
        # Given
        existing = make_server(auth_type=McpAuthType.NONE)
        use_case, deps = _build_use_case(existing_server=existing)

        # When
        await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
        )

        # Then
        deps["crypto"].decrypt.assert_not_called()  # type: ignore[attr-defined]
        deps["mcp_client"].list_tools.assert_awaited_once_with(  # type: ignore[attr-defined]
            url=existing.url, bearer_token=None
        )

    async def test_refresh_not_found_raises(self) -> None:
        # Given
        use_case, _ = _build_use_case(existing_server=None)

        # When / Then
        with pytest.raises(McpServerNotFoundError):
            await use_case.execute(server_id=uuid4(), organization_id=uuid4(), user_id=uuid4())

    async def test_refresh_access_denied_for_user_role(self) -> None:
        # Given
        existing = make_server()
        use_case, _ = _build_use_case(member_role=OrganizationMemberRole.USER, existing_server=existing)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                server_id=existing.id,
                organization_id=existing.organization_id,
                user_id=uuid4(),
            )

    async def test_refresh_handshake_error_propagates(self) -> None:
        # Given
        existing = make_server()
        use_case, deps = _build_use_case(existing_server=existing, handshake_raises=McpHandshakeError("502"))

        # When / Then
        with pytest.raises(McpHandshakeError):
            await use_case.execute(
                server_id=existing.id,
                organization_id=existing.organization_id,
                user_id=uuid4(),
            )
        deps["server_repo"].save.assert_not_awaited()  # type: ignore[attr-defined]
