class McpServerNotFoundError(Exception):
    """Raised when an MCP server cannot be found."""


class McpDuplicateSlugError(ValueError):
    """Raised when an MCP server slug is already taken in the organization."""


class McpAccessDeniedError(PermissionError):
    """Raised when a user cannot manage MCP servers for an organization."""


class McpUrlForbiddenError(ValueError):
    """Raised when an MCP server URL is rejected (non-HTTPS, private IP, denylisted host)."""


class McpHandshakeError(Exception):
    """Raised when the initial `tools/list` handshake with an MCP server fails."""


class McpToolNotFoundError(Exception):
    """Raised when a tool requested for invocation is not present in the snapshot."""


class McpCallTimeoutError(Exception):
    """Raised when an MCP tool call exceeds its timeout."""
