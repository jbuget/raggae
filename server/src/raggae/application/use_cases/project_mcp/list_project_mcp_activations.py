from uuid import UUID

from raggae.application.dto.project_mcp_activation_view_dto import ProjectMcpActivationViewDTO
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
from raggae.application.use_cases.org_mcp._mapping import to_dto
from raggae.application.use_cases.project_mcp._access import load_project_for_user


class ListProjectMcpActivations:
    """Use case: list MCP servers available to a project with their activation status."""

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

    async def execute(self, project_id: UUID, user_id: UUID) -> list[ProjectMcpActivationViewDTO]:
        project = await load_project_for_user(
            project_id=project_id,
            user_id=user_id,
            project_repository=self._project_repository,
            organization_member_repository=self._member_repository,
        )
        if project.organization_id is None:
            return []

        org_servers = await self._org_mcp_server_repository.list_by_org_id(project.organization_id)
        activations = await self._activation_repository.list_by_project_id(project_id)
        activation_by_server = {a.org_mcp_server_id: a for a in activations}

        views: list[ProjectMcpActivationViewDTO] = []
        for server in org_servers:
            if not server.is_active:
                continue
            activation = activation_by_server.get(server.id)
            views.append(
                ProjectMcpActivationViewDTO(
                    org_mcp_server=to_dto(server),
                    is_activated=activation is not None and activation.is_active,
                )
            )
        return views
