from dataclasses import dataclass

from raggae.application.dto.org_mcp_server_dto import OrgMcpServerDTO


@dataclass(frozen=True)
class ProjectMcpActivationViewDTO:
    """Aggregated view of an MCP server with its activation status for a project."""

    org_mcp_server: OrgMcpServerDTO
    is_activated: bool
