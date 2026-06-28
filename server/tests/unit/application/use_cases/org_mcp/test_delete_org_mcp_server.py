from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_mcp.delete_org_mcp_server import DeleteOrgMcpServer
from raggae.domain.exceptions.mcp_exceptions import McpServerNotFoundError
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

from ._helpers import make_member, make_server


def _build_use_case(
    *,
    member_role: OrganizationMemberRole | None,
    existing_server: object | None,
) -> tuple[DeleteOrgMcpServer, dict[str, AsyncMock]]:
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    server_repo = AsyncMock()
    server_repo.find_by_id = AsyncMock(return_value=existing_server)
    server_repo.delete = AsyncMock()
    activation_repo = AsyncMock()
    activation_repo.delete_by_org_mcp_server_id = AsyncMock()
    use_case = DeleteOrgMcpServer(
        org_mcp_server_repository=server_repo,
        organization_member_repository=member_repo,
        project_mcp_activation_repository=activation_repo,
    )
    return use_case, {
        "server_repo": server_repo,
        "activation_repo": activation_repo,
    }


class TestDeleteOrgMcpServer:
    async def test_delete_cascades_activations_then_server(self) -> None:
        # Given
        existing = make_server()
        use_case, deps = _build_use_case(member_role=OrganizationMemberRole.OWNER, existing_server=existing)

        # When
        await use_case.execute(
            server_id=existing.id,
            organization_id=existing.organization_id,
            user_id=uuid4(),
        )

        # Then — activations supprimées AVANT le serveur
        deps["activation_repo"].delete_by_org_mcp_server_id.assert_awaited_once_with(existing.id)
        deps["server_repo"].delete.assert_awaited_once_with(existing.id, existing.organization_id)

    async def test_delete_not_found_raises(self) -> None:
        # Given
        use_case, deps = _build_use_case(member_role=OrganizationMemberRole.OWNER, existing_server=None)

        # When / Then
        with pytest.raises(McpServerNotFoundError):
            await use_case.execute(server_id=uuid4(), organization_id=uuid4(), user_id=uuid4())
        deps["activation_repo"].delete_by_org_mcp_server_id.assert_not_awaited()
        deps["server_repo"].delete.assert_not_awaited()

    async def test_delete_access_denied_for_user_role(self) -> None:
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
