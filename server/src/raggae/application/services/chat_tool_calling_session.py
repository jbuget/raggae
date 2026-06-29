"""Drives a single tool-calling exchange between the LLM and MCP servers.

Given a structured message list and a list of available MCP tools, this service
sends the conversation to a `ToolCapableLLMService` and, when the LLM requests
tool calls, executes them via `McpToolExecutor`, appends the tool results to
the conversation, and loops until the LLM returns a text answer (or the max
iteration cap is hit). Each tool failure is folded back into the conversation
as a tool result so the LLM can react gracefully.
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from raggae.application.interfaces.services.tool_capable_llm_service import (
    ToolCapableLLMService,
)
from raggae.application.services.mcp_tool_executor import McpToolExecutor
from raggae.domain.value_objects.chat_message import ChatMessage, ChatRole
from raggae.domain.value_objects.llm_response import LLMTextResponse, LLMToolCallResponse
from raggae.domain.value_objects.llm_tool_descriptor import LLMToolDescriptor
from raggae.domain.value_objects.mcp_tool_descriptor import McpToolDescriptor

logger = logging.getLogger(__name__)

_DEFAULT_MAX_ITERATIONS = 6


@dataclass(frozen=True)
class ToolCallingResult:
    """Result of a tool-calling exchange."""

    final_answer: str
    tool_invocations: list[str] = field(default_factory=list)  # prefixed tool names invoked
    iterations: int = 0


class ChatToolCallingSession:
    def __init__(
        self,
        llm_service: ToolCapableLLMService,
        tool_executor: McpToolExecutor,
        max_iterations: int = _DEFAULT_MAX_ITERATIONS,
    ) -> None:
        self._llm_service = llm_service
        self._tool_executor = tool_executor
        self._max_iterations = max(1, max_iterations)

    async def run(
        self,
        messages: list[ChatMessage],
        mcp_tools: list[McpToolDescriptor],
        llm_tools: list[LLMToolDescriptor],
        organization_id: UUID,
    ) -> ToolCallingResult:
        history: list[ChatMessage] = list(messages)
        invocations: list[str] = []
        tools_by_name = {tool.prefixed_name: tool for tool in mcp_tools}

        for iteration in range(1, self._max_iterations + 1):
            response = await self._llm_service.generate_with_tools(messages=history, tools=llm_tools)
            if isinstance(response, LLMTextResponse):
                return ToolCallingResult(
                    final_answer=response.text,
                    tool_invocations=invocations,
                    iterations=iteration,
                )
            if not isinstance(response, LLMToolCallResponse):
                # Defensive: unknown response type, stop the loop.
                return ToolCallingResult(
                    final_answer="",
                    tool_invocations=invocations,
                    iterations=iteration,
                )

            history.append(
                ChatMessage(
                    role=ChatRole.ASSISTANT,
                    content=None,
                    tool_calls=response.tool_calls,
                )
            )
            for tool_call in response.tool_calls:
                invocations.append(tool_call.name)
                descriptor = tools_by_name.get(tool_call.name)
                if descriptor is None:
                    history.append(
                        ChatMessage(
                            role=ChatRole.TOOL,
                            content=json.dumps({"error": f"Unknown tool '{tool_call.name}'"}),
                            tool_call_id=tool_call.id,
                            name=tool_call.name,
                        )
                    )
                    continue
                tool_result_payload = await self._invoke_tool(
                    descriptor=descriptor,
                    arguments=tool_call.arguments,
                    organization_id=organization_id,
                )
                history.append(
                    ChatMessage(
                        role=ChatRole.TOOL,
                        content=json.dumps(tool_result_payload),
                        tool_call_id=tool_call.id,
                        name=tool_call.name,
                    )
                )

        logger.warning(
            "chat_tool_calling_max_iterations_reached",
            extra={"iterations": self._max_iterations, "invocations": invocations},
        )
        return ToolCallingResult(
            final_answer=(
                "I tried to call several tools but did not converge to a final answer. "
                "Please rephrase your request."
            ),
            tool_invocations=invocations,
            iterations=self._max_iterations,
        )

    async def _invoke_tool(
        self,
        descriptor: McpToolDescriptor,
        arguments: dict[str, Any],
        organization_id: UUID,
    ) -> dict[str, Any]:
        try:
            return await self._tool_executor.execute(
                descriptor=descriptor,
                arguments=arguments,
                organization_id=organization_id,
            )
        except Exception as exc:  # noqa: BLE001 — we deliberately surface to the LLM
            logger.warning(
                "chat_tool_invocation_failed",
                extra={
                    "tool_name": descriptor.prefixed_name,
                    "error": str(exc),
                },
            )
            return {"error": str(exc)}
