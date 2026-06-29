"""Value objects describing messages exchanged with a tool-capable LLM.

These types replace the single-string `prompt` used by `LLMService.generate_answer`
once a conversation enters a tool-calling loop. Each conversation step is now a
structured `ChatMessage`, and the LLM can return either a final text answer or
one-or-more tool calls.
"""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ChatRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass(frozen=True)
class ToolCall:
    """One tool invocation requested by the LLM during a tool-calling round."""

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ChatMessage:
    """Single message in a tool-capable LLM conversation.

    - SYSTEM / USER / ASSISTANT: `content` carries the text. ASSISTANT may also
      carry `tool_calls` (without `content`) when the model decided to call tools
      rather than respond.
    - TOOL: response to a previous ToolCall; `tool_call_id` references the
      assistant's ToolCall.id, and `name` is the tool's prefixed name.
    """

    role: ChatRole
    content: str | None = None
    tool_calls: list[ToolCall] = field(default_factory=list)
    tool_call_id: str | None = None
    name: str | None = None
