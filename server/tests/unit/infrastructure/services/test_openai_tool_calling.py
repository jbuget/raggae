"""Unit tests for OpenAILLMService.generate_with_tools.

We patch the AsyncOpenAI client to avoid any network call and verify both the
shape of the payload sent to OpenAI and the parsing of the response into
domain `LLMResponse` value objects.
"""

import json
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

from raggae.domain.value_objects.chat_message import ChatMessage, ChatRole, ToolCall
from raggae.domain.value_objects.llm_response import LLMTextResponse, LLMToolCallResponse
from raggae.domain.value_objects.llm_tool_descriptor import LLMToolDescriptor
from raggae.infrastructure.services.openai_llm_service import OpenAILLMService


def _make_service(create_mock: AsyncMock) -> OpenAILLMService:
    service = OpenAILLMService(api_key="sk-test", model="gpt-4o-mini")
    # Patch the inner AsyncOpenAI client directly to keep type checkers happy
    service._client = SimpleNamespace(  # type: ignore[assignment]
        chat=SimpleNamespace(completions=SimpleNamespace(create=create_mock))
    )
    return service


def _openai_text_response(text: str) -> Any:
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text, tool_calls=None))])


def _openai_tool_call_response(name: str, arguments: dict[str, Any], call_id: str = "call_1") -> Any:
    function = SimpleNamespace(name=name, arguments=json.dumps(arguments))
    tool_call = SimpleNamespace(id=call_id, function=function)
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=None, tool_calls=[tool_call]))]
    )


class TestOpenAIGenerateWithTools:
    async def test_returns_text_response_when_model_answers(self) -> None:
        # Given
        create_mock = AsyncMock(return_value=_openai_text_response("Hello"))
        service = _make_service(create_mock)

        # When
        result = await service.generate_with_tools(
            messages=[ChatMessage(role=ChatRole.USER, content="Hi")],
            tools=[],
        )

        # Then
        assert isinstance(result, LLMTextResponse)
        assert result.text == "Hello"

    async def test_returns_tool_call_response_when_model_calls_a_tool(self) -> None:
        # Given
        create_mock = AsyncMock(
            return_value=_openai_tool_call_response(
                name="notion__search", arguments={"q": "report"}, call_id="call_xyz"
            )
        )
        service = _make_service(create_mock)
        descriptor = LLMToolDescriptor(
            name="notion__search",
            description="Search Notion",
            parameters={"type": "object", "properties": {"q": {"type": "string"}}},
        )

        # When
        result = await service.generate_with_tools(
            messages=[ChatMessage(role=ChatRole.USER, content="search the report")],
            tools=[descriptor],
        )

        # Then
        assert isinstance(result, LLMToolCallResponse)
        assert len(result.tool_calls) == 1
        assert result.tool_calls[0].id == "call_xyz"
        assert result.tool_calls[0].name == "notion__search"
        assert result.tool_calls[0].arguments == {"q": "report"}

    async def test_payload_uses_openai_tool_format(self) -> None:
        # Given
        create_mock = AsyncMock(return_value=_openai_text_response(""))
        service = _make_service(create_mock)
        descriptor = LLMToolDescriptor(
            name="notion__search",
            description="Search",
            parameters={"type": "object", "properties": {"q": {"type": "string"}}},
        )

        # When
        await service.generate_with_tools(
            messages=[ChatMessage(role=ChatRole.USER, content="hi")],
            tools=[descriptor],
        )

        # Then
        kwargs = create_mock.await_args.kwargs
        assert kwargs["model"] == "gpt-4o-mini"
        assert kwargs["messages"] == [{"role": "user", "content": "hi"}]
        assert kwargs["tools"] == [
            {
                "type": "function",
                "function": {
                    "name": "notion__search",
                    "description": "Search",
                    "parameters": {
                        "type": "object",
                        "properties": {"q": {"type": "string"}},
                    },
                },
            }
        ]

    async def test_serializes_assistant_message_with_tool_calls(self) -> None:
        # Given
        create_mock = AsyncMock(return_value=_openai_text_response("done"))
        service = _make_service(create_mock)
        assistant_msg = ChatMessage(
            role=ChatRole.ASSISTANT,
            content=None,
            tool_calls=[ToolCall(id="call_1", name="notion__search", arguments={"q": "hi"})],
        )

        # When
        await service.generate_with_tools(
            messages=[
                ChatMessage(role=ChatRole.USER, content="search"),
                assistant_msg,
                ChatMessage(
                    role=ChatRole.TOOL,
                    content='{"result":"ok"}',
                    tool_call_id="call_1",
                    name="notion__search",
                ),
            ],
            tools=[],
        )

        # Then — assistant message carries serialized tool_calls
        kwargs = create_mock.await_args.kwargs
        sent_messages = kwargs["messages"]
        assert sent_messages[1]["role"] == "assistant"
        assert sent_messages[1]["tool_calls"][0]["function"]["name"] == "notion__search"
        assert sent_messages[1]["tool_calls"][0]["function"]["arguments"] == '{"q": "hi"}'
        # Tool reply message is well-formed
        assert sent_messages[2]["role"] == "tool"
        assert sent_messages[2]["tool_call_id"] == "call_1"
        assert sent_messages[2]["content"] == '{"result":"ok"}'

    async def test_empty_tools_list_sends_no_tools_param(self) -> None:
        # Given
        create_mock = AsyncMock(return_value=_openai_text_response("hi"))
        service = _make_service(create_mock)

        # When
        await service.generate_with_tools(
            messages=[ChatMessage(role=ChatRole.USER, content="hi")],
            tools=[],
        )

        # Then
        kwargs = create_mock.await_args.kwargs
        assert kwargs["tools"] is None

    async def test_invalid_arguments_json_falls_back_to_empty_dict(self) -> None:
        # Given — defensive parsing when the model returns malformed JSON
        function = SimpleNamespace(name="notion__search", arguments="not json")
        tool_call = SimpleNamespace(id="call_1", function=function)
        bad_response = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=None, tool_calls=[tool_call]))]
        )
        create_mock = AsyncMock(return_value=bad_response)
        service = _make_service(create_mock)

        # When
        result = await service.generate_with_tools(
            messages=[ChatMessage(role=ChatRole.USER, content="hi")],
            tools=[],
        )

        # Then
        assert isinstance(result, LLMToolCallResponse)
        assert result.tool_calls[0].arguments == {}
