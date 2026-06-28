from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_mcp.list_org_mcp_servers import ListOrgMcpServers
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole

from ._helpers import make_member, make_server


def _build_use_case(
    *,
    member_role: OrganizationMemberRole | None,
    servers: list[object] | None = None,
) -> ListOrgMcpServers:
    member_repo = AsyncMock()
    member_repo.find_by_organization_and_user = AsyncMock(
        return_value=(make_member(member_role) if member_role is not None else None)
    )
    server_repo = AsyncMock()
    server_repo.list_by_org_id = AsyncMock(return_value=servers or [])
    return ListOrgMcpServers(
        org_mcp_server_repository=server_repo,
        organization_member_repository=member_repo,
    )


class TestListOrgMcpServers:
    async def test_list_succeeds_for_any_member(self) -> None:
        # Given
        org_id = uuid4()
        servers = [make_server(organization_id=org_id, name="A", slug="a")]
        use_case = _build_use_case(member_role=OrganizationMemberRole.USER, servers=servers)

        # When
        result = await use_case.execute(organization_id=org_id, user_id=uuid4())

        # Then
        assert len(result) == 1
        assert result[0].slug == "a"

    async def test_list_denied_for_non_member(self) -> None:
        # Given
        use_case = _build_use_case(member_role=None)

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())
