from uuid import UUID

from raggae.application.dto.org_mcp_server_dto import OrgMcpServerDTO
from raggae.application.interfaces.repositories.org_mcp_server_repository import (
    OrgMcpServerRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.use_cases.org_mcp._mapping import to_dto
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError


class ListOrgMcpServers:
    """Use case: list all MCP servers declared by an organization."""

    def __init__(
        self,
        org_mcp_server_repository: OrgMcpServerRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._server_repository = org_mcp_server_repository
        self._member_repository = organization_member_repository

    async def execute(self, organization_id: UUID, user_id: UUID) -> list[OrgMcpServerDTO]:
        member = await self._member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None:
            raise OrganizationAccessDeniedError(
                f"User {user_id} is not a member of organization {organization_id}"
            )
        servers = await self._server_repository.list_by_org_id(organization_id)
        return [to_dto(s) for s in servers]
