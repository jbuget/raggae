from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_mcp.update_org_mcp_server import UpdateOrgMcpServer
from raggae.domain.exceptions.mcp_exceptions import (
    McpServerNotFoundError,
    McpUrlForbiddenError,
)
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

from ._helpers import make_member, make_server


def _build_use_case(
    *,
    member_role: OrganizationMemberRole | None = OrganizationMemberRole.OWNER,
    existing_server: object | None = None,
) -> tuple[UpdateOrgMcpServer, dict[str, object]]:
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    server_repo = AsyncMock()
    server_repo.find_by_id = AsyncMock(return_value=existing_server)
    server_repo.save = AsyncMock()
    url_validator = AsyncMock()
    url_validator.validate = AsyncMock(return_value=None)
    crypto = Mock()
    crypto.encrypt.return_value = "encrypted-new"
    crypto.fingerprint.return_value = "fp-new"
    use_case = UpdateOrgMcpServer(
        org_mcp_server_repository=server_repo,
        organization_member_repository=member_repo,
        url_safety_validator=url_validator,
        bearer_token_crypto_service=crypto,
    )
    return use_case, {
        "server_repo": server_repo,
        "url_validator": url_validator,
        "crypto": crypto,
    }


class TestUpdateOrgMcpServer:
    async def test_update_name_url_timeout(self) -> None:
        # Given
        org_id = uuid4()
        server_id = uuid4()
        existing = make_server(server_id=server_id, organization_id=org_id, name="Old", timeout_seconds=30)
        use_case, deps = _build_use_case(existing_server=existing)

        # When
        result = await use_case.execute(
            server_id=server_id,
            organization_id=org_id,
            user_id=uuid4(),
            name="New",
            url="https://new.example.com",
            timeout_seconds=20,
            auth_type=None,
            bearer_token=None,
        )

        # Then
        assert result.name == "New"
        assert result.url == "https://new.example.com"
        assert result.timeout_seconds == 20
        deps["url_validator"].validate.assert_awaited_once_with("https://new.example.com")  # type: ignore[attr-defined]
        deps["server_repo"].save.assert_awaited_once()  # type: ignore[attr-defined]

    async def test_update_changes_auth_to_bearer(self) -> None:
        # Given
        existing = make_server(auth_type=McpAuthType.NONE)
        use_case, deps = _build_use_case(existing_server=existing)

        # When
        result = await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
            name=existing.name,
            url=existing.url,
            timeout_seconds=existing.timeout_seconds,
            auth_type="bearer",
            bearer_token="new-token-abcd",
        )

        # Then
        assert result.auth_type == "bearer"
        assert result.masked_token == "...abcd"
        deps["crypto"].encrypt.assert_called_once_with("new-token-abcd")  # type: ignore[attr-defined]

    async def test_update_removes_auth(self) -> None:
        # Given
        existing = make_server(auth_type=McpAuthType.BEARER)
        use_case, _ = _build_use_case(existing_server=existing)

        # When
        result = await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
            name=existing.name,
            url=existing.url,
            timeout_seconds=existing.timeout_seconds,
            auth_type="none",
            bearer_token=None,
        )

        # Then
        assert result.auth_type == "none"
        assert result.masked_token is None

    async def test_update_preserves_existing_bearer_when_auth_type_unchanged(self) -> None:
        # Given
        existing = make_server(auth_type=McpAuthType.BEARER)
        use_case, deps = _build_use_case(existing_server=existing)

        # When
        result = await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
            name="Renamed",
            url=existing.url,
            timeout_seconds=existing.timeout_seconds,
            auth_type=None,
            bearer_token=None,
        )

        # Then — token preserved, crypto NOT called
        assert result.auth_type == "bearer"
        assert result.masked_token == "...abcd"
        deps["crypto"].encrypt.assert_not_called()  # type: ignore[attr-defined]

    async def test_update_access_denied_for_user_role(self) -> None:
        # Given
        existing = make_server()
        use_case, _ = _build_use_case(member_role=OrganizationMemberRole.USER, existing_server=existing)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                server_id=existing.id,
                organization_id=existing.organization_id,
                user_id=uuid4(),
                name="X",
                url="https://x",
                timeout_seconds=30,
                auth_type=None,
                bearer_token=None,
            )

    async def test_update_not_found_raises(self) -> None:
        # Given
        use_case, _ = _build_use_case(existing_server=None)

        # When / Then
        with pytest.raises(McpServerNotFoundError):
            await use_case.execute(
                server_id=uuid4(),
                organization_id=uuid4(),
                user_id=uuid4(),
                name="X",
                url="https://x",
                timeout_seconds=30,
                auth_type=None,
                bearer_token=None,
            )

    async def test_update_invalid_timeout_raises(self) -> None:
        # Given
        existing = make_server()
        use_case, _ = _build_use_case(existing_server=existing)

        # When / Then
        with pytest.raises(ValueError):
            await use_case.execute(
                server_id=existing.id,
                organization_id=existing.organization_id,
                user_id=uuid4(),
                name=existing.name,
                url=existing.url,
                timeout_seconds=999,
                auth_type=None,
                bearer_token=None,
            )

    async def test_update_url_validates_only_when_changed(self) -> None:
        # Given
        existing = make_server(url="https://same.example.com")
        use_case, deps = _build_use_case(existing_server=existing)

        # When
        await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
            name=existing.name,
            url="https://same.example.com",
            timeout_seconds=existing.timeout_seconds,
            auth_type=None,
            bearer_token=None,
        )

        # Then — URL unchanged, validator not called
        deps["url_validator"].validate.assert_not_awaited()  # type: ignore[attr-defined]

    async def test_update_rejects_forbidden_url(self) -> None:
        # Given
        existing = make_server()
        use_case, deps = _build_use_case(existing_server=existing)
        deps["url_validator"].validate = AsyncMock(  # type: ignore[attr-defined]
            side_effect=McpUrlForbiddenError("blocked")
        )

        # When / Then
        with pytest.raises(McpUrlForbiddenError):
            await use_case.execute(
                server_id=existing.id,
                organization_id=existing.organization_id,
                user_id=uuid4(),
                name=existing.name,
                url="http://localhost:9999",
                timeout_seconds=existing.timeout_seconds,
                auth_type=None,
                bearer_token=None,
            )
