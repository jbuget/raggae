from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class LLMToolDescriptor:
    """Description of one tool exposed to a tool-capable LLM.

    `name` is the identifier the LLM will use when calling the tool back
    (typically the MCP prefixed name `<slug>__<tool_name>`). `parameters` is a
    JSON Schema describing the arguments.
    """

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
