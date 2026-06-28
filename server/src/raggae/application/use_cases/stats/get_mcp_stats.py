from raggae.application.dto.mcp_stats_dto import McpStatsDTO
from raggae.application.interfaces.repositories.org_mcp_server_repository import (
    OrgMcpServerRepository,
)
from raggae.application.interfaces.repositories.project_mcp_activation_repository import (
    ProjectMcpActivationRepository,
)


class GetMcpStats:
    """Use case: aggregate platform-level MCP stats (servers + project activations)."""

    def __init__(
        self,
        org_mcp_server_repository: OrgMcpServerRepository,
        project_mcp_activation_repository: ProjectMcpActivationRepository,
    ) -> None:
        self._server_repository = org_mcp_server_repository
        self._activation_repository = project_mcp_activation_repository

    async def execute(self) -> McpStatsDTO:
        return McpStatsDTO(
            org_servers_total=await self._server_repository.count_all(),
            org_servers_active=await self._server_repository.count_active(),
            project_activations_active=(await self._activation_repository.count_active_activations()),
            projects_with_at_least_one_activation=(
                await self._activation_repository.count_distinct_active_projects()
            ),
        )
