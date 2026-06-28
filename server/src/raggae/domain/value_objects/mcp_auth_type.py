from enum import StrEnum


class McpAuthType(StrEnum):
    """Supported authentication types for an MCP server."""

    NONE = "none"
    BEARER = "bearer"
