from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_mcp.activate_org_mcp_server import ActivateOrgMcpServer
from raggae.application.use_cases.org_mcp.deactivate_org_mcp_server import DeactivateOrgMcpServer
from raggae.domain.exceptions.mcp_exceptions import McpServerNotFoundError
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

from ._helpers import make_member, make_server


def _build_deps(
    *,
    member_role: OrganizationMemberRole | None,
    existing_server: object | None,
) -> tuple[AsyncMock, AsyncMock]:
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    server_repo = AsyncMock()
    server_repo.find_by_id = AsyncMock(return_value=existing_server)
    server_repo.save = AsyncMock()
    return server_repo, member_repo


class TestActivateOrgMcpServer:
    async def test_activate_sets_is_active_true_and_persists(self) -> None:
        # Given
        existing = make_server(is_active=False)
        server_repo, member_repo = _build_deps(
            member_role=OrganizationMemberRole.OWNER, existing_server=existing
        )
        use_case = ActivateOrgMcpServer(
            org_mcp_server_repository=server_repo,
            organization_member_repository=member_repo,
        )

        # When
        await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
        )

        # Then
        server_repo.save.assert_awaited_once()
        saved = server_repo.save.await_args.args[0]
        assert saved.is_active is True

    async def test_activate_not_found_raises(self) -> None:
        # Given
        server_repo, member_repo = _build_deps(member_role=OrganizationMemberRole.OWNER, existing_server=None)
        use_case = ActivateOrgMcpServer(
            org_mcp_server_repository=server_repo,
            organization_member_repository=member_repo,
        )

        # When / Then
        with pytest.raises(McpServerNotFoundError):
            await use_case.execute(server_id=uuid4(), organization_id=uuid4(), user_id=uuid4())

    async def test_activate_access_denied_for_user_role(self) -> None:
        # Given
        existing = make_server()
        server_repo, member_repo = _build_deps(
            member_role=OrganizationMemberRole.USER, existing_server=existing
        )
        use_case = ActivateOrgMcpServer(
            org_mcp_server_repository=server_repo,
            organization_member_repository=member_repo,
        )

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                server_id=existing.id,
                organization_id=existing.organization_id,
                user_id=uuid4(),
            )


class TestDeactivateOrgMcpServer:
    async def test_deactivate_sets_is_active_false_and_persists(self) -> None:
        # Given
        existing = make_server(is_active=True)
        server_repo, member_repo = _build_deps(
            member_role=OrganizationMemberRole.MAKER, existing_server=existing
        )
        use_case = DeactivateOrgMcpServer(
            org_mcp_server_repository=server_repo,
            organization_member_repository=member_repo,
        )

        # When
        await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
        )

        # Then
        server_repo.save.assert_awaited_once()
        saved = server_repo.save.await_args.args[0]
        assert saved.is_active is False
