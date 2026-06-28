from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_mcp.declare_org_mcp_server import DeclareOrgMcpServer
from raggae.domain.exceptions.mcp_exceptions import (
    McpHandshakeError,
    McpUrlForbiddenError,
)
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

from ._helpers import make_member, make_server


def _build_use_case(
    *,
    member_role: OrganizationMemberRole | None = OrganizationMemberRole.OWNER,
    existing_servers: list[object] | None = None,
    existing_by_slug: dict[str, object] | None = None,
    handshake_tools: list[McpToolSnapshot] | None = None,
    handshake_raises: Exception | None = None,
    url_validator_raises: Exception | None = None,
) -> tuple[DeclareOrgMcpServer, dict[str, object]]:
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    server_repo = AsyncMock()
    server_repo.list_by_org_id = AsyncMock(return_value=existing_servers or [])

    async def _find_by_slug(_org_id: object, slug: str) -> object | None:
        return (existing_by_slug or {}).get(slug)

    server_repo.find_by_slug = AsyncMock(side_effect=_find_by_slug)
    server_repo.save = AsyncMock()
    url_validator = AsyncMock()
    if url_validator_raises is not None:
        url_validator.validate = AsyncMock(side_effect=url_validator_raises)
    else:
        url_validator.validate = AsyncMock(return_value=None)
    mcp_client = AsyncMock()
    if handshake_raises is not None:
        mcp_client.list_tools = AsyncMock(side_effect=handshake_raises)
    else:
        mcp_client.list_tools = AsyncMock(return_value=handshake_tools or [])
    crypto = Mock()
    crypto.encrypt.return_value = "encrypted-value"
    crypto.fingerprint.return_value = "fp123"

    use_case = DeclareOrgMcpServer(
        org_mcp_server_repository=server_repo,
        organization_member_repository=member_repo,
        url_safety_validator=url_validator,
        mcp_client=mcp_client,
        bearer_token_crypto_service=crypto,
    )
    deps: dict[str, object] = {
        "member_repo": member_repo,
        "server_repo": server_repo,
        "url_validator": url_validator,
        "mcp_client": mcp_client,
        "crypto": crypto,
    }
    return use_case, deps


class TestDeclareOrgMcpServer:
    async def test_declare_success_as_owner_with_no_auth(self) -> None:
        # Given
        tools = [McpToolSnapshot(name="search", description="Search", input_schema={})]
        use_case, deps = _build_use_case(handshake_tools=tools)

        # When
        result = await use_case.execute(
            organization_id=uuid4(),
            user_id=uuid4(),
            name="Notion",
            url="https://mcp.example.com",
            auth_type="none",
            bearer_token=None,
            timeout_seconds=30,
        )

        # Then
        assert result.name == "Notion"
        assert result.slug == "notion"
        assert result.url == "https://mcp.example.com"
        assert result.auth_type == "none"
        assert result.masked_token is None
        assert result.is_active is True
        assert len(result.tools_snapshot) == 1
        assert result.tools_snapshot[0].name == "search"
        deps["server_repo"].save.assert_awaited_once()  # type: ignore[attr-defined]
        deps["url_validator"].validate.assert_awaited_once()  # type: ignore[attr-defined]

    async def test_declare_success_as_maker_with_bearer(self) -> None:
        # Given
        use_case, deps = _build_use_case(member_role=OrganizationMemberRole.MAKER)

        # When
        result = await use_case.execute(
            organization_id=uuid4(),
            user_id=uuid4(),
            name="GitHub",
            url="https://mcp.github.com",
            auth_type="bearer",
            bearer_token="gh-token-wxyz",
            timeout_seconds=15,
        )

        # Then
        assert result.auth_type == "bearer"
        assert result.masked_token == "...wxyz"
        deps["crypto"].encrypt.assert_called_once_with("gh-token-wxyz")  # type: ignore[attr-defined]
        deps["crypto"].fingerprint.assert_called_once_with("gh-token-wxyz")  # type: ignore[attr-defined]

    async def test_declare_access_denied_for_user_role(self) -> None:
        # Given
        use_case, _ = _build_use_case(member_role=OrganizationMemberRole.USER)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                name="Notion",
                url="https://mcp.example.com",
                auth_type="none",
                bearer_token=None,
                timeout_seconds=30,
            )

    async def test_declare_access_denied_for_non_member(self) -> None:
        # Given
        use_case, _ = _build_use_case(member_role=None)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                name="Notion",
                url="https://mcp.example.com",
                auth_type="none",
                bearer_token=None,
                timeout_seconds=30,
            )

    async def test_declare_rejected_url_raises(self) -> None:
        # Given
        use_case, deps = _build_use_case(url_validator_raises=McpUrlForbiddenError("blocked"))

        # When / Then
        with pytest.raises(McpUrlForbiddenError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                name="Bad",
                url="http://localhost:8080",
                auth_type="none",
                bearer_token=None,
                timeout_seconds=30,
            )
        deps["server_repo"].save.assert_not_awaited()  # type: ignore[attr-defined]
        deps["mcp_client"].list_tools.assert_not_awaited()  # type: ignore[attr-defined]

    async def test_declare_handshake_error_propagates(self) -> None:
        # Given
        use_case, deps = _build_use_case(handshake_raises=McpHandshakeError("502"))

        # When / Then
        with pytest.raises(McpHandshakeError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                name="Notion",
                url="https://mcp.example.com",
                auth_type="none",
                bearer_token=None,
                timeout_seconds=30,
            )
        deps["server_repo"].save.assert_not_awaited()  # type: ignore[attr-defined]

    async def test_declare_rejects_invalid_timeout(self) -> None:
        # Given
        use_case, _ = _build_use_case()

        # When / Then
        with pytest.raises(ValueError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                name="Notion",
                url="https://mcp.example.com",
                auth_type="none",
                bearer_token=None,
                timeout_seconds=4,
            )
        with pytest.raises(ValueError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                name="Notion",
                url="https://mcp.example.com",
                auth_type="none",
                bearer_token=None,
                timeout_seconds=120,
            )

    async def test_declare_rejects_bearer_without_token(self) -> None:
        # Given
        use_case, _ = _build_use_case()

        # When / Then
        with pytest.raises(ValueError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                name="Notion",
                url="https://mcp.example.com",
                auth_type="bearer",
                bearer_token=None,
                timeout_seconds=30,
            )

    async def test_declare_appends_numeric_suffix_on_slug_collision(self) -> None:
        # Given
        org_id = uuid4()
        existing_a = make_server(organization_id=org_id, name="Notion", slug="notion")
        existing_b = make_server(organization_id=org_id, name="Notion v2", slug="notion-2")
        use_case, _ = _build_use_case(existing_by_slug={"notion": existing_a, "notion-2": existing_b})

        # When
        result = await use_case.execute(
            organization_id=org_id,
            user_id=uuid4(),
            name="Notion",
            url="https://mcp.example.com",
            auth_type="none",
            bearer_token=None,
            timeout_seconds=30,
        )

        # Then
        assert result.slug == "notion-3"

    async def test_declare_passes_bearer_token_to_handshake(self) -> None:
        # Given
        use_case, deps = _build_use_case()

        # When
        await use_case.execute(
            organization_id=uuid4(),
            user_id=uuid4(),
            name="GitHub",
            url="https://mcp.github.com",
            auth_type="bearer",
            bearer_token="gh-token-1234",
            timeout_seconds=30,
        )

        # Then
        deps["mcp_client"].list_tools.assert_awaited_once_with(  # type: ignore[attr-defined]
            url="https://mcp.github.com", bearer_token="gh-token-1234"
        )

    async def test_declare_invalid_auth_type_raises(self) -> None:
        # Given
        use_case, _ = _build_use_case()

        # When / Then
        with pytest.raises(ValueError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                name="X",
                url="https://x",
                auth_type="oauth",
                bearer_token=None,
                timeout_seconds=30,
            )

    async def test_declare_default_auth_type_resolved_to_enum(self) -> None:
        # Given
        use_case, _ = _build_use_case()

        # When
        result = await use_case.execute(
            organization_id=uuid4(),
            user_id=uuid4(),
            name="X",
            url="https://x",
            auth_type=McpAuthType.NONE.value,
            bearer_token=None,
            timeout_seconds=30,
        )

        # Then
        assert result.auth_type == "none"
