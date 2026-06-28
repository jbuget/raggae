from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.project_mcp.list_project_mcp_activations import (
    ListProjectMcpActivations,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

from ._helpers import make_activation, make_member, make_project, make_server


def _build_use_case(
    *,
    project,
    member_role: OrganizationMemberRole | None = OrganizationMemberRole.MAKER,
    org_servers: list[object] | None = None,
    activations: list[object] | None = None,
) -> ListProjectMcpActivations:
    project_repo = AsyncMock()
    project_repo.find_by_id = AsyncMock(return_value=project)
    server_repo = AsyncMock()
    server_repo.list_by_org_id = AsyncMock(return_value=org_servers or [])
    activation_repo = AsyncMock()
    activation_repo.list_by_project_id = AsyncMock(return_value=activations or [])
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    return ListProjectMcpActivations(
        project_repository=project_repo,
        org_mcp_server_repository=server_repo,
        project_mcp_activation_repository=activation_repo,
        organization_member_repository=member_repo,
    )


class TestListProjectMcpActivations:
    async def test_returns_only_active_org_servers_with_activation_status(self) -> None:
        # Given
        org_id = uuid4()
        project = make_project(organization_id=org_id)
        active_server = make_server(organization_id=org_id, slug="notion", is_active=True)
        inactive_server = make_server(organization_id=org_id, slug="archived", is_active=False)
        activation = make_activation(project_id=project.id, server_id=active_server.id, is_active=True)
        use_case = _build_use_case(
            project=project,
            org_servers=[active_server, inactive_server],
            activations=[activation],
        )

        # When
        result = await use_case.execute(project_id=project.id, user_id=uuid4())

        # Then — only the active server is exposed, with its activation status
        assert len(result) == 1
        assert result[0].org_mcp_server.slug == "notion"
        assert result[0].is_activated is True

    async def test_marks_server_as_not_activated_when_no_activation_row(self) -> None:
        # Given
        org_id = uuid4()
        project = make_project(organization_id=org_id)
        server = make_server(organization_id=org_id)
        use_case = _build_use_case(project=project, org_servers=[server], activations=[])

        # When
        result = await use_case.execute(project_id=project.id, user_id=uuid4())

        # Then
        assert len(result) == 1
        assert result[0].is_activated is False

    async def test_marks_server_as_not_activated_when_activation_is_false(self) -> None:
        # Given
        org_id = uuid4()
        project = make_project(organization_id=org_id)
        server = make_server(organization_id=org_id)
        activation = make_activation(project_id=project.id, server_id=server.id, is_active=False)
        use_case = _build_use_case(project=project, org_servers=[server], activations=[activation])

        # When
        result = await use_case.execute(project_id=project.id, user_id=uuid4())

        # Then
        assert result[0].is_activated is False

    async def test_returns_empty_list_for_user_owned_project(self) -> None:
        # Given
        project = make_project(organization_id=None)  # user-owned, no org
        use_case = _build_use_case(project=project, org_servers=[], activations=[])

        # When
        result = await use_case.execute(project_id=project.id, user_id=project.user_id)

        # Then
        assert result == []

    async def test_raises_when_project_does_not_exist(self) -> None:
        # Given
        use_case = _build_use_case(project=None)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=uuid4(), user_id=uuid4())

    async def test_raises_when_user_has_no_access_to_org_project(self) -> None:
        # Given
        project = make_project(organization_id=uuid4())
        use_case = _build_use_case(project=project, member_role=None)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, user_id=uuid4())

    async def test_user_who_owns_the_project_can_list_without_org_membership(self) -> None:
        # Given — user-owned project, user is owner, no org context
        owner_id = uuid4()
        project = make_project(user_id=owner_id, organization_id=None)
        use_case = _build_use_case(project=project, member_role=None)

        # When
        result = await use_case.execute(project_id=project.id, user_id=owner_id)

        # Then
        assert result == []
