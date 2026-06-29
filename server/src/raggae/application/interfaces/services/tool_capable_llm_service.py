from typing import Protocol, runtime_checkable

from raggae.domain.value_objects.chat_message import ChatMessage
from raggae.domain.value_objects.llm_response import LLMResponse
from raggae.domain.value_objects.llm_tool_descriptor import LLMToolDescriptor


@runtime_checkable
class ToolCapableLLMService(Protocol):
    """Optional extension of `LLMService` for providers that support tool calling.

    A concrete LLM adapter may implement both `LLMService` (the legacy single-prompt
    interface) and `ToolCapableLLMService`. Use `isinstance(service,
    ToolCapableLLMService)` at runtime to know whether tools can be exposed to it.
    """

    async def generate_with_tools(
        self,
        messages: list[ChatMessage],
        tools: list[LLMToolDescriptor],
    ) -> LLMResponse:
        """Send a structured conversation with available tools.

        Returns either an `LLMTextResponse` (final answer) or an
        `LLMToolCallResponse` (one or more tool calls to execute before
        continuing the loop).
        """
        ...
