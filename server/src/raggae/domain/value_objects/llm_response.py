from dataclasses import dataclass, field

from raggae.domain.value_objects.chat_message import ToolCall


@dataclass(frozen=True)
class LLMTextResponse:
    """The LLM returned a final textual answer."""

    text: str


@dataclass(frozen=True)
class LLMToolCallResponse:
    """The LLM requested one or more tool invocations before producing a final answer."""

    tool_calls: list[ToolCall] = field(default_factory=list)


LLMResponse = LLMTextResponse | LLMToolCallResponse
