from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class McpToolDescriptor:
    """Runtime descriptor of one MCP tool exposed to a project's LLM.

    The `prefixed_name` is the identifier the LLM sees (`<server_slug>__<tool_name>`);
    the `original_name` is what we send back to the MCP server during tool calls.
    """

    mcp_server_id: UUID
    mcp_server_slug: str
    original_name: str
    prefixed_name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
    server_url: str = ""
    has_bearer_token: bool = False
    timeout_seconds: int = 30
