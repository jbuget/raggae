from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ProjectMcpActivation:
    """Activation of one organization MCP server by one project. Immutable."""

    project_id: UUID
    org_mcp_server_id: UUID
    is_active: bool
    activated_at: datetime
    activated_by_user_id: UUID

    def activate(self) -> "ProjectMcpActivation":
        return replace(self, is_active=True)

    def deactivate(self) -> "ProjectMcpActivation":
        return replace(self, is_active=False)
