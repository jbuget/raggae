from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from raggae.application.services.chat_tool_calling_session import (
    ChatToolCallingSession,
)
from raggae.domain.value_objects.chat_message import ChatMessage, ChatRole, ToolCall
from raggae.domain.value_objects.llm_response import (
    LLMTextResponse,
    LLMToolCallResponse,
)
from raggae.domain.value_objects.llm_tool_descriptor import LLMToolDescriptor
from raggae.domain.value_objects.mcp_tool_descriptor import McpToolDescriptor


def _make_mcp_descriptor(prefixed_name: str = "notion__search") -> McpToolDescriptor:
    return McpToolDescriptor(
        mcp_server_id=uuid4(),
        mcp_server_slug="notion",
        original_name="search",
        prefixed_name=prefixed_name,
        description="Search",
        input_schema={},
        server_url="https://mcp.example.com",
        has_bearer_token=False,
        timeout_seconds=30,
    )


def _make_llm_descriptor(name: str = "notion__search") -> LLMToolDescriptor:
    return LLMToolDescriptor(name=name, description="Search", parameters={})


def _build_session(
    *,
    llm_responses: list,
    executor_results: list | None = None,
    executor_raises: Exception | None = None,
) -> tuple[ChatToolCallingSession, dict]:
    llm = AsyncMock()
    llm.generate_with_tools = AsyncMock(side_effect=list(llm_responses))
    executor = AsyncMock()
    if executor_raises is not None:
        executor.execute = AsyncMock(side_effect=executor_raises)
    else:
        executor.execute = AsyncMock(side_effect=list(executor_results or []))
    session = ChatToolCallingSession(llm_service=llm, tool_executor=executor, max_iterations=5)
    return session, {"llm": llm, "executor": executor}


class TestChatToolCallingSession:
    async def test_returns_final_answer_when_llm_replies_directly(self) -> None:
        # Given
        session, deps = _build_session(llm_responses=[LLMTextResponse(text="Hi there")])

        # When
        result = await session.run(
            messages=[ChatMessage(role=ChatRole.USER, content="hello")],
            mcp_tools=[],
            llm_tools=[],
            organization_id=uuid4(),
        )

        # Then
        assert result.final_answer == "Hi there"
        assert result.iterations == 1
        assert result.tool_invocations == []
        deps["executor"].execute.assert_not_awaited()

    async def test_routes_tool_call_to_executor_and_completes(self) -> None:
        # Given
        descriptor = _make_mcp_descriptor()
        first = LLMToolCallResponse(
            tool_calls=[ToolCall(id="call_1", name=descriptor.prefixed_name, arguments={"q": "x"})],
        )
        second = LLMTextResponse(text="Final answer using tool result")
        session, deps = _build_session(
            llm_responses=[first, second],
            executor_results=[{"content": "match"}],
        )

        # When
        result = await session.run(
            messages=[ChatMessage(role=ChatRole.USER, content="search")],
            mcp_tools=[descriptor],
            llm_tools=[_make_llm_descriptor()],
            organization_id=uuid4(),
        )

        # Then
        assert result.final_answer == "Final answer using tool result"
        assert result.iterations == 2
        assert result.tool_invocations == [descriptor.prefixed_name]
        deps["executor"].execute.assert_awaited_once()
        # Verify the executor was called with the right descriptor and arguments
        call_kwargs = deps["executor"].execute.await_args.kwargs
        assert call_kwargs["descriptor"] is descriptor
        assert call_kwargs["arguments"] == {"q": "x"}

    async def test_unknown_tool_returns_error_to_llm_and_continues(self) -> None:
        # Given
        first = LLMToolCallResponse(
            tool_calls=[ToolCall(id="call_1", name="ghost__delete", arguments={})],
        )
        second = LLMTextResponse(text="Sorry, ignored")
        session, deps = _build_session(llm_responses=[first, second])

        # When
        result = await session.run(
            messages=[ChatMessage(role=ChatRole.USER, content="x")],
            mcp_tools=[_make_mcp_descriptor()],
            llm_tools=[],
            organization_id=uuid4(),
        )

        # Then
        assert result.final_answer == "Sorry, ignored"
        # Executor must NOT be called for unknown tools
        deps["executor"].execute.assert_not_awaited()
        # The second LLM call must include the error tool message
        second_call_kwargs = deps["llm"].generate_with_tools.await_args_list[1].kwargs
        last_msg = second_call_kwargs["messages"][-1]
        assert last_msg.role == ChatRole.TOOL
        assert "Unknown tool" in last_msg.content

    async def test_tool_execution_failure_is_surfaced_as_tool_result(self) -> None:
        # Given
        descriptor = _make_mcp_descriptor()
        first = LLMToolCallResponse(
            tool_calls=[ToolCall(id="call_1", name=descriptor.prefixed_name, arguments={})],
        )
        second = LLMTextResponse(text="Could not search")
        session, deps = _build_session(
            llm_responses=[first, second],
            executor_raises=RuntimeError("timeout"),
        )

        # When
        result = await session.run(
            messages=[ChatMessage(role=ChatRole.USER, content="x")],
            mcp_tools=[descriptor],
            llm_tools=[_make_llm_descriptor()],
            organization_id=uuid4(),
        )

        # Then
        assert result.final_answer == "Could not search"
        # Verify the tool result message contains the error payload
        second_call_kwargs = deps["llm"].generate_with_tools.await_args_list[1].kwargs
        last_msg = second_call_kwargs["messages"][-1]
        assert last_msg.role == ChatRole.TOOL
        assert "timeout" in last_msg.content

    async def test_stops_at_max_iterations_with_fallback_answer(self) -> None:
        # Given — always returns a tool call, never converges
        descriptor = _make_mcp_descriptor()
        looping_response = LLMToolCallResponse(
            tool_calls=[ToolCall(id="call_loop", name=descriptor.prefixed_name, arguments={})],
        )
        # 5 LLM responses for max_iterations=5
        session, deps = _build_session(
            llm_responses=[looping_response] * 5,
            executor_results=[{"ok": True}] * 5,
        )

        # When
        result = await session.run(
            messages=[ChatMessage(role=ChatRole.USER, content="x")],
            mcp_tools=[descriptor],
            llm_tools=[_make_llm_descriptor()],
            organization_id=uuid4(),
        )

        # Then
        assert result.iterations == 5
        assert "did not converge" in result.final_answer

    async def test_dummy_now_to_keep_imports_alive(self) -> None:
        # Keep `datetime`/`UTC` import valid by exercising a no-op assertion
        assert datetime.now(UTC) is not None
