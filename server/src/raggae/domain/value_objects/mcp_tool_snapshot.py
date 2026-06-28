from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class McpToolSnapshot:
    """Snapshot of one tool exposed by an MCP server, as returned by `tools/list`."""

    name: str
    description: str
    input_schema: dict[str, Any] = field(default_factory=dict)
