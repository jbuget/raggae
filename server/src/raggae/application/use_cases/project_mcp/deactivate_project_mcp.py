from uuid import UUID

from raggae.application.interfaces.repositories.org_mcp_server_repository import (
    OrgMcpServerRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_mcp_activation_repository import (
    ProjectMcpActivationRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.use_cases.project_mcp._access import load_project_for_user
from raggae.domain.exceptions.mcp_exceptions import (
    McpAccessDeniedError,
    McpServerNotFoundError,
)


class DeactivateProjectMcp:
    """Use case: deactivate one MCP server for a project (deletes the activation row)."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        org_mcp_server_repository: OrgMcpServerRepository,
        project_mcp_activation_repository: ProjectMcpActivationRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._project_repository = project_repository
        self._org_mcp_server_repository = org_mcp_server_repository
        self._activation_repository = project_mcp_activation_repository
        self._member_repository = organization_member_repository

    async def execute(self, project_id: UUID, mcp_server_id: UUID, user_id: UUID) -> None:
        project = await load_project_for_user(
            project_id=project_id,
            user_id=user_id,
            project_repository=self._project_repository,
            organization_member_repository=self._member_repository,
        )
        if project.organization_id is None:
            raise McpAccessDeniedError(f"Project {project_id} has no organization and cannot use MCP servers")

        server = await self._org_mcp_server_repository.find_by_id(mcp_server_id, project.organization_id)
        if server is None:
            raise McpServerNotFoundError(f"MCP server {mcp_server_id} not found")

        await self._activation_repository.delete(project_id, mcp_server_id)
