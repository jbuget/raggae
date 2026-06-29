"""LLM adapter for Anthropic Claude (messages API).

Implements `LLMService` (single-prompt text generation) and
`ToolCapableLLMService` (structured conversation with tool calling) using the
Anthropic Python SDK. The mapping between our domain `ChatMessage` and
Anthropic's payload follows the official `messages.create` schema:
https://docs.anthropic.com/en/api/messages
"""

import logging
from collections.abc import AsyncIterator
from time import perf_counter
from typing import Any

from anthropic import AsyncAnthropic

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.domain.value_objects.chat_message import ChatMessage, ChatRole, ToolCall
from raggae.domain.value_objects.llm_response import (
    LLMResponse,
    LLMTextResponse,
    LLMToolCallResponse,
)
from raggae.domain.value_objects.llm_tool_descriptor import LLMToolDescriptor

logger = logging.getLogger(__name__)

_DEFAULT_MAX_TOKENS = 4096


class AnthropicLLMService:
    """LLM service implementation backed by Anthropic Claude messages API."""

    def __init__(self, api_key: str, model: str, max_tokens: int = _DEFAULT_MAX_TOKENS) -> None:
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = model
        self._max_tokens = max_tokens

    async def generate_answer(self, prompt: str) -> str:
        started_at = perf_counter()
        logger.info(
            "llm_request_started",
            extra={"backend": "anthropic", "model": self._model},
        )
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            text = _extract_text_from_content_blocks(response.content)
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_request_succeeded",
                extra={
                    "backend": "anthropic",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            return text
        except Exception as exc:  # pragma: no cover - provider dependent
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_request_failed",
                extra={
                    "backend": "anthropic",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc

    async def generate_answer_stream(self, prompt: str) -> AsyncIterator[str]:
        # Streaming not yet wired into the chat use case; expose the same one-shot
        # answer as a single chunk to keep the LLMService contract honored.
        text = await self.generate_answer(prompt)
        yield text

    async def generate_with_tools(
        self,
        messages: list[ChatMessage],
        tools: list[LLMToolDescriptor],
    ) -> LLMResponse:
        system_prompt = _extract_system_prompt(messages)
        anthropic_messages = _build_anthropic_messages(messages)
        anthropic_tools = [_tool_to_anthropic(t) for t in tools] if tools else None

        started_at = perf_counter()
        logger.info(
            "llm_tools_request_started",
            extra={"backend": "anthropic", "model": self._model, "tools_count": len(tools)},
        )
        try:
            kwargs: dict[str, Any] = {
                "model": self._model,
                "max_tokens": self._max_tokens,
                "messages": anthropic_messages,
            }
            if system_prompt is not None:
                kwargs["system"] = system_prompt
            if anthropic_tools is not None:
                kwargs["tools"] = anthropic_tools
            response = await self._client.messages.create(**kwargs)
        except Exception as exc:
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_tools_request_failed",
                extra={
                    "backend": "anthropic",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to generate with tools: {exc}") from exc

        elapsed_ms = (perf_counter() - started_at) * 1000.0
        logger.info(
            "llm_tools_request_succeeded",
            extra={
                "backend": "anthropic",
                "model": self._model,
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )

        tool_calls = _extract_tool_calls(response.content)
        if tool_calls:
            return LLMToolCallResponse(tool_calls=tool_calls)
        return LLMTextResponse(text=_extract_text_from_content_blocks(response.content))


def _extract_system_prompt(messages: list[ChatMessage]) -> str | None:
    """Anthropic carries the system prompt as a top-level `system` argument."""
    system_parts = [m.content or "" for m in messages if m.role == ChatRole.SYSTEM and m.content]
    if not system_parts:
        return None
    return "\n\n".join(system_parts)


def _build_anthropic_messages(messages: list[ChatMessage]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for message in messages:
        if message.role == ChatRole.SYSTEM:
            continue
        if message.role == ChatRole.TOOL:
            output.append(
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": message.tool_call_id or "",
                            "content": message.content or "",
                        }
                    ],
                }
            )
            continue
        if message.role == ChatRole.ASSISTANT and message.tool_calls:
            blocks: list[dict[str, Any]] = []
            if message.content:
                blocks.append({"type": "text", "text": message.content})
            for tc in message.tool_calls:
                blocks.append(
                    {
                        "type": "tool_use",
                        "id": tc.id,
                        "name": tc.name,
                        "input": tc.arguments,
                    }
                )
            output.append({"role": "assistant", "content": blocks})
            continue
        output.append({"role": message.role.value, "content": message.content or ""})
    return output


def _tool_to_anthropic(tool: LLMToolDescriptor) -> dict[str, Any]:
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.parameters or {"type": "object", "properties": {}},
    }


def _extract_text_from_content_blocks(blocks: Any) -> str:
    parts: list[str] = []
    for block in blocks or []:
        block_type = getattr(block, "type", None)
        if block_type == "text":
            parts.append(getattr(block, "text", "") or "")
    return "".join(parts)


def _extract_tool_calls(blocks: Any) -> list[ToolCall]:
    tool_calls: list[ToolCall] = []
    for block in blocks or []:
        if getattr(block, "type", None) != "tool_use":
            continue
        arguments = getattr(block, "input", None) or {}
        if not isinstance(arguments, dict):
            arguments = {}
        tool_calls.append(
            ToolCall(
                id=getattr(block, "id", ""),
                name=getattr(block, "name", ""),
                arguments=arguments,
            )
        )
    return tool_calls
