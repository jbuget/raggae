from dataclasses import dataclass


@dataclass(frozen=True)
class McpStatsDTO:
    """Platform-level aggregated stats for MCP usage."""

    org_servers_total: int
    org_servers_active: int
    project_activations_active: int
    projects_with_at_least_one_activation: int
