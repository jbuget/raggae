import json
import logging
from collections.abc import AsyncIterator
from time import perf_counter
from typing import Any

from openai import AsyncOpenAI

from raggae.domain.exceptions.document_exceptions import LLMGenerationError
from raggae.domain.value_objects.chat_message import ChatMessage, ChatRole, ToolCall
from raggae.domain.value_objects.llm_response import (
    LLMResponse,
    LLMTextResponse,
    LLMToolCallResponse,
)
from raggae.domain.value_objects.llm_tool_descriptor import LLMToolDescriptor

logger = logging.getLogger(__name__)


class OpenAILLMService:
    """LLM service implementation backed by OpenAI chat completions.

    Implements both `LLMService` (single-prompt text generation) and
    `ToolCapableLLMService` (structured conversation with tool calling).
    """

    def __init__(self, api_key: str, model: str) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model

    async def generate_answer(self, prompt: str) -> str:
        started_at = perf_counter()
        logger.info(
            "llm_request_started",
            extra={"backend": "openai", "model": self._model},
        )
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.choices[0].message.content
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_request_succeeded",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            return content or ""
        except Exception as exc:  # pragma: no cover - provider dependent
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_request_failed",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to generate answer: {exc}") from exc

    async def generate_answer_stream(self, prompt: str) -> AsyncIterator[str]:
        started_at = perf_counter()
        logger.info(
            "llm_stream_started",
            extra={"backend": "openai", "model": self._model},
        )
        try:
            stream = await self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
            )
            async for chunk in stream:
                delta = chunk.choices[0].delta.content if chunk.choices else None
                if delta:
                    yield delta
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.info(
                "llm_stream_succeeded",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
        except Exception as exc:  # pragma: no cover - provider dependent
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_stream_failed",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to stream answer: {exc}") from exc

    async def generate_with_tools(
        self,
        messages: list[ChatMessage],
        tools: list[LLMToolDescriptor],
    ) -> LLMResponse:
        openai_messages = [_message_to_openai(m) for m in messages]
        openai_tools = [_tool_to_openai(t) for t in tools] if tools else None

        started_at = perf_counter()
        logger.info(
            "llm_tools_request_started",
            extra={"backend": "openai", "model": self._model, "tools_count": len(tools)},
        )
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=openai_messages,  # type: ignore[arg-type]
                tools=openai_tools,  # type: ignore[arg-type]
            )
        except Exception as exc:
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "llm_tools_request_failed",
                extra={
                    "backend": "openai",
                    "model": self._model,
                    "elapsed_ms": round(elapsed_ms, 2),
                },
            )
            raise LLMGenerationError(f"Failed to generate with tools: {exc}") from exc

        elapsed_ms = (perf_counter() - started_at) * 1000.0
        logger.info(
            "llm_tools_request_succeeded",
            extra={
                "backend": "openai",
                "model": self._model,
                "elapsed_ms": round(elapsed_ms, 2),
            },
        )
        choice = response.choices[0].message
        raw_tool_calls = getattr(choice, "tool_calls", None) or []
        if raw_tool_calls:
            return LLMToolCallResponse(
                tool_calls=[_openai_tool_call_to_domain(tc) for tc in raw_tool_calls],
            )
        return LLMTextResponse(text=choice.content or "")


def _message_to_openai(message: ChatMessage) -> dict[str, Any]:
    if message.role == ChatRole.TOOL:
        return {
            "role": "tool",
            "tool_call_id": message.tool_call_id or "",
            "content": message.content or "",
        }
    if message.role == ChatRole.ASSISTANT and message.tool_calls:
        return {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments),
                    },
                }
                for tc in message.tool_calls
            ],
        }
    return {"role": message.role.value, "content": message.content or ""}


def _tool_to_openai(tool: LLMToolDescriptor) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.parameters or {"type": "object", "properties": {}},
        },
    }


def _openai_tool_call_to_domain(raw_tool_call: Any) -> ToolCall:
    args_raw = raw_tool_call.function.arguments if raw_tool_call.function else "{}"
    try:
        arguments = json.loads(args_raw) if args_raw else {}
    except json.JSONDecodeError:
        arguments = {}
    return ToolCall(
        id=raw_tool_call.id,
        name=raw_tool_call.function.name if raw_tool_call.function else "",
        arguments=arguments,
    )
