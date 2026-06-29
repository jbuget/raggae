from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

from raggae.domain.value_objects.chat_message import ChatMessage, ChatRole, ToolCall
from raggae.domain.value_objects.llm_response import LLMTextResponse, LLMToolCallResponse
from raggae.domain.value_objects.llm_tool_descriptor import LLMToolDescriptor
from raggae.infrastructure.services.anthropic_llm_service import AnthropicLLMService


def _make_service(create_mock: AsyncMock) -> AnthropicLLMService:
    service = AnthropicLLMService(api_key="sk-ant", model="claude-3-5-sonnet")
    service._client = SimpleNamespace(  # type: ignore[assignment]
        messages=SimpleNamespace(create=create_mock)
    )
    return service


def _text_response(text: str) -> Any:
    return SimpleNamespace(content=[SimpleNamespace(type="text", text=text)])


def _tool_use_response(name: str, arguments: dict[str, Any], call_id: str = "toolu_1") -> Any:
    return SimpleNamespace(content=[SimpleNamespace(type="tool_use", id=call_id, name=name, input=arguments)])


class TestAnthropicGenerateWithTools:
    async def test_returns_text_response(self) -> None:
        create_mock = AsyncMock(return_value=_text_response("Hello"))
        service = _make_service(create_mock)

        result = await service.generate_with_tools(
            messages=[ChatMessage(role=ChatRole.USER, content="Hi")],
            tools=[],
        )

        assert isinstance(result, LLMTextResponse)
        assert result.text == "Hello"

    async def test_returns_tool_call_response(self) -> None:
        create_mock = AsyncMock(
            return_value=_tool_use_response(name="notion__search", arguments={"q": "x"}, call_id="toolu_xyz")
        )
        service = _make_service(create_mock)

        result = await service.generate_with_tools(
            messages=[ChatMessage(role=ChatRole.USER, content="search")],
            tools=[
                LLMToolDescriptor(
                    name="notion__search",
                    description="Search",
                    parameters={"type": "object", "properties": {"q": {"type": "string"}}},
                )
            ],
        )

        assert isinstance(result, LLMToolCallResponse)
        assert result.tool_calls[0].id == "toolu_xyz"
        assert result.tool_calls[0].name == "notion__search"
        assert result.tool_calls[0].arguments == {"q": "x"}

    async def test_extracts_system_prompt_to_top_level(self) -> None:
        create_mock = AsyncMock(return_value=_text_response("ok"))
        service = _make_service(create_mock)

        await service.generate_with_tools(
            messages=[
                ChatMessage(role=ChatRole.SYSTEM, content="You are helpful."),
                ChatMessage(role=ChatRole.USER, content="hi"),
            ],
            tools=[],
        )

        kwargs = create_mock.await_args.kwargs
        assert kwargs["system"] == "You are helpful."
        # The system message must NOT appear in the messages array
        assert all(m["role"] != "system" for m in kwargs["messages"])

    async def test_tool_use_then_tool_result_round_trip(self) -> None:
        # Given — an assistant message with a tool_use followed by a tool result
        create_mock = AsyncMock(return_value=_text_response("final"))
        service = _make_service(create_mock)

        await service.generate_with_tools(
            messages=[
                ChatMessage(role=ChatRole.USER, content="search docs"),
                ChatMessage(
                    role=ChatRole.ASSISTANT,
                    content=None,
                    tool_calls=[ToolCall(id="toolu_1", name="notion__search", arguments={"q": "report"})],
                ),
                ChatMessage(
                    role=ChatRole.TOOL,
                    content='{"hits":[]}',
                    tool_call_id="toolu_1",
                    name="notion__search",
                ),
            ],
            tools=[],
        )

        kwargs = create_mock.await_args.kwargs
        msgs = kwargs["messages"]
        # Assistant message carries a tool_use block
        assistant = next(m for m in msgs if m["role"] == "assistant")
        assert assistant["content"][0]["type"] == "tool_use"
        assert assistant["content"][0]["id"] == "toolu_1"
        assert assistant["content"][0]["input"] == {"q": "report"}
        # Tool result is folded into a user message with tool_result block
        tool_user = msgs[-1]
        assert tool_user["role"] == "user"
        assert tool_user["content"][0]["type"] == "tool_result"
        assert tool_user["content"][0]["tool_use_id"] == "toolu_1"
        assert tool_user["content"][0]["content"] == '{"hits":[]}'

    async def test_tools_are_serialized_to_anthropic_format(self) -> None:
        create_mock = AsyncMock(return_value=_text_response(""))
        service = _make_service(create_mock)

        await service.generate_with_tools(
            messages=[ChatMessage(role=ChatRole.USER, content="hi")],
            tools=[
                LLMToolDescriptor(
                    name="notion__search",
                    description="Search Notion",
                    parameters={"type": "object", "properties": {"q": {"type": "string"}}},
                )
            ],
        )

        kwargs = create_mock.await_args.kwargs
        assert kwargs["tools"] == [
            {
                "name": "notion__search",
                "description": "Search Notion",
                "input_schema": {
                    "type": "object",
                    "properties": {"q": {"type": "string"}},
                },
            }
        ]
