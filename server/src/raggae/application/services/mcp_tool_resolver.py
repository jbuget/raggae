"""Resolves the list of MCP tools available to a project at chat-time.

The resolver fans out from a project_id to:
- the project's organization,
- the activations marked `is_active=true` on that project,
- the org MCP servers `is_active=true` referenced by those activations,
- the flattened list of tools, each prefixed by the server slug
  (`<slug>__<tool_name>`) so that names from different MCPs cannot collide.
"""

from uuid import UUID

from raggae.application.interfaces.repositories.org_mcp_server_repository import (
    OrgMcpServerRepository,
)
from raggae.application.interfaces.repositories.project_mcp_activation_repository import (
    ProjectMcpActivationRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_descriptor import McpToolDescriptor

_TOOL_PREFIX_SEPARATOR = "__"


class McpToolResolver:
    """Application service: aggregates active MCP tools available to a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        org_mcp_server_repository: OrgMcpServerRepository,
        project_mcp_activation_repository: ProjectMcpActivationRepository,
    ) -> None:
        self._project_repository = project_repository
        self._org_mcp_server_repository = org_mcp_server_repository
        self._activation_repository = project_mcp_activation_repository

    async def resolve(self, project_id: UUID) -> list[McpToolDescriptor]:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.organization_id is None:
            return []

        activations = await self._activation_repository.list_by_project_id(project_id)
        active_server_ids = {
            activation.org_mcp_server_id for activation in activations if activation.is_active
        }
        if not active_server_ids:
            return []

        descriptors: list[McpToolDescriptor] = []
        for server_id in active_server_ids:
            server = await self._org_mcp_server_repository.find_by_id(server_id, project.organization_id)
            if server is None or not server.is_active:
                continue
            for tool in server.tools_snapshot:
                descriptors.append(
                    McpToolDescriptor(
                        mcp_server_id=server.id,
                        mcp_server_slug=server.slug,
                        original_name=tool.name,
                        prefixed_name=f"{server.slug}{_TOOL_PREFIX_SEPARATOR}{tool.name}",
                        description=tool.description,
                        input_schema=tool.input_schema,
                        server_url=server.url,
                        has_bearer_token=server.auth_type == McpAuthType.BEARER,
                        timeout_seconds=server.timeout_seconds,
                    )
                )
        return descriptors

    @staticmethod
    def split_prefixed_name(prefixed_name: str) -> tuple[str, str] | None:
        """Inverse of the prefix encoding. Returns `(slug, tool_name)` or None."""
        if _TOOL_PREFIX_SEPARATOR not in prefixed_name:
            return None
        slug, _, original = prefixed_name.partition(_TOOL_PREFIX_SEPARATOR)
        if not slug or not original:
            return None
        return slug, original
