from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.project_mcp.activate_project_mcp import ActivateProjectMcp
from raggae.application.use_cases.project_mcp.deactivate_project_mcp import DeactivateProjectMcp
from raggae.domain.exceptions.mcp_exceptions import (
    McpAccessDeniedError,
    McpServerNotFoundError,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

from ._helpers import make_member, make_project, make_server


def _build_activate(
    *,
    project,
    org_server: object | None = None,
    member_role: OrganizationMemberRole | None = OrganizationMemberRole.MAKER,
) -> tuple[ActivateProjectMcp, dict[str, AsyncMock]]:
    project_repo = AsyncMock()
    project_repo.find_by_id = AsyncMock(return_value=project)
    server_repo = AsyncMock()
    server_repo.find_by_id = AsyncMock(return_value=org_server)
    activation_repo = AsyncMock()
    activation_repo.save = AsyncMock()
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    use_case = ActivateProjectMcp(
        project_repository=project_repo,
        org_mcp_server_repository=server_repo,
        project_mcp_activation_repository=activation_repo,
        organization_member_repository=member_repo,
    )
    return use_case, {
        "activation_repo": activation_repo,
        "server_repo": server_repo,
    }


def _build_deactivate(
    *,
    project,
    org_server: object | None = None,
    member_role: OrganizationMemberRole | None = OrganizationMemberRole.MAKER,
) -> tuple[DeactivateProjectMcp, dict[str, AsyncMock]]:
    project_repo = AsyncMock()
    project_repo.find_by_id = AsyncMock(return_value=project)
    server_repo = AsyncMock()
    server_repo.find_by_id = AsyncMock(return_value=org_server)
    activation_repo = AsyncMock()
    activation_repo.delete = AsyncMock()
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    use_case = DeactivateProjectMcp(
        project_repository=project_repo,
        org_mcp_server_repository=server_repo,
        project_mcp_activation_repository=activation_repo,
        organization_member_repository=member_repo,
    )
    return use_case, {
        "activation_repo": activation_repo,
        "server_repo": server_repo,
    }


class TestActivateProjectMcp:
    async def test_activate_persists_activation(self) -> None:
        # Given
        org_id = uuid4()
        project = make_project(organization_id=org_id)
        server = make_server(organization_id=org_id)
        use_case, deps = _build_activate(project=project, org_server=server)

        # When
        await use_case.execute(project_id=project.id, mcp_server_id=server.id, user_id=uuid4())

        # Then
        deps["activation_repo"].save.assert_awaited_once()
        saved = deps["activation_repo"].save.await_args.args[0]
        assert saved.project_id == project.id
        assert saved.org_mcp_server_id == server.id
        assert saved.is_active is True

    async def test_activate_raises_when_server_not_found(self) -> None:
        # Given
        project = make_project(organization_id=uuid4())
        use_case, _ = _build_activate(project=project, org_server=None)

        # When / Then
        with pytest.raises(McpServerNotFoundError):
            await use_case.execute(project_id=project.id, mcp_server_id=uuid4(), user_id=uuid4())

    async def test_activate_raises_when_server_scoped_lookup_returns_none(self) -> None:
        # Given — the repo `find_by_id` is scoped by `organization_id`; a server that
        # belongs to a different org cannot be loaded for this project and is treated
        # as "not found".
        project = make_project(organization_id=uuid4())
        use_case, _ = _build_activate(project=project, org_server=None)

        # When / Then
        with pytest.raises(McpServerNotFoundError):
            await use_case.execute(project_id=project.id, mcp_server_id=uuid4(), user_id=uuid4())

    async def test_activate_raises_when_server_is_inactive_at_org_level(self) -> None:
        # Given
        org_id = uuid4()
        project = make_project(organization_id=org_id)
        server = make_server(organization_id=org_id, is_active=False)
        use_case, _ = _build_activate(project=project, org_server=server)

        # When / Then
        with pytest.raises(McpAccessDeniedError):
            await use_case.execute(project_id=project.id, mcp_server_id=server.id, user_id=uuid4())

    async def test_activate_raises_when_user_has_no_access_to_project(self) -> None:
        # Given
        project = make_project(organization_id=uuid4())
        server = make_server(organization_id=project.organization_id)
        use_case, _ = _build_activate(project=project, org_server=server, member_role=None)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, mcp_server_id=server.id, user_id=uuid4())

    async def test_activate_raises_when_project_is_user_owned_only(self) -> None:
        # Given — a user-owned project cannot use org MCPs
        owner_id = uuid4()
        project = make_project(user_id=owner_id, organization_id=None)
        server = make_server()  # any org
        use_case, _ = _build_activate(project=project, org_server=server, member_role=None)

        # When / Then
        with pytest.raises(McpAccessDeniedError):
            await use_case.execute(project_id=project.id, mcp_server_id=server.id, user_id=owner_id)

    async def test_activate_uses_current_timestamp(self) -> None:
        # Given
        org_id = uuid4()
        project = make_project(organization_id=org_id)
        server = make_server(organization_id=org_id)
        use_case, deps = _build_activate(project=project, org_server=server)
        before = datetime.now(UTC)

        # When
        await use_case.execute(project_id=project.id, mcp_server_id=server.id, user_id=uuid4())

        # Then
        saved = deps["activation_repo"].save.await_args.args[0]
        assert saved.activated_at >= before


class TestDeactivateProjectMcp:
    async def test_deactivate_deletes_activation(self) -> None:
        # Given
        org_id = uuid4()
        project = make_project(organization_id=org_id)
        server = make_server(organization_id=org_id)
        use_case, deps = _build_deactivate(project=project, org_server=server)

        # When
        await use_case.execute(project_id=project.id, mcp_server_id=server.id, user_id=uuid4())

        # Then
        deps["activation_repo"].delete.assert_awaited_once_with(project.id, server.id)

    async def test_deactivate_raises_when_server_scoped_lookup_returns_none(self) -> None:
        # Given
        project = make_project(organization_id=uuid4())
        use_case, _ = _build_deactivate(project=project, org_server=None)

        # When / Then
        with pytest.raises(McpServerNotFoundError):
            await use_case.execute(project_id=project.id, mcp_server_id=uuid4(), user_id=uuid4())

    async def test_deactivate_is_idempotent_when_no_activation_exists(self) -> None:
        # Given — the activation may not exist; the use case still completes.
        org_id = uuid4()
        project = make_project(organization_id=org_id)
        server = make_server(organization_id=org_id)
        use_case, deps = _build_deactivate(project=project, org_server=server)

        # When
        await use_case.execute(project_id=project.id, mcp_server_id=server.id, user_id=uuid4())

        # Then — delete called even if there was nothing to delete (repo no-ops)
        deps["activation_repo"].delete.assert_awaited_once()
