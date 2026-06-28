import json
from typing import Any
from unittest.mock import AsyncMock

import httpx
import pytest

from raggae.domain.exceptions.mcp_exceptions import (
    McpCallTimeoutError,
    McpHandshakeError,
    McpToolNotFoundError,
    McpUrlForbiddenError,
)
from raggae.infrastructure.services.http_mcp_client import HttpMcpClient


def _json_response(payload: dict[str, Any], status: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status,
        headers={"Content-Type": "application/json"},
        content=json.dumps(payload).encode("utf-8"),
    )


def _sse_response(payload: dict[str, Any]) -> httpx.Response:
    body = f"event: message\ndata: {json.dumps(payload)}\n\n"
    return httpx.Response(
        status_code=200,
        headers={"Content-Type": "text/event-stream"},
        content=body.encode("utf-8"),
    )


def _make_client(*, transport: httpx.MockTransport) -> HttpMcpClient:
    url_validator = AsyncMock()
    url_validator.validate = AsyncMock(return_value=None)
    return HttpMcpClient(
        url_safety_validator=url_validator,
        http_client_factory=lambda: httpx.AsyncClient(transport=transport),
    )


class TestHttpMcpClientListTools:
    async def test_list_tools_parses_json_rpc_response(self) -> None:
        # Given
        seen_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen_request["url"] = str(request.url)
            seen_request["headers"] = dict(request.headers)
            seen_request["body"] = json.loads(request.content.decode("utf-8"))
            return _json_response(
                {
                    "jsonrpc": "2.0",
                    "id": seen_request["body"]["id"],
                    "result": {
                        "tools": [
                            {
                                "name": "search",
                                "description": "Search documents",
                                "inputSchema": {"type": "object"},
                            }
                        ]
                    },
                }
            )

        client = _make_client(transport=httpx.MockTransport(handler))

        # When
        tools = await client.list_tools(url="https://mcp.example.com/")

        # Then
        assert len(tools) == 1
        assert tools[0].name == "search"
        assert tools[0].input_schema == {"type": "object"}
        assert seen_request["body"]["method"] == "tools/list"
        assert "application/json" in seen_request["headers"]["accept"]

    async def test_list_tools_attaches_bearer_token(self) -> None:
        # Given
        seen_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen_request["authorization"] = request.headers.get("authorization")
            return _json_response({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})

        client = _make_client(transport=httpx.MockTransport(handler))

        # When
        await client.list_tools(url="https://mcp.example.com/", bearer_token="my-token")

        # Then
        assert seen_request["authorization"] == "Bearer my-token"

    async def test_list_tools_supports_sse_response(self) -> None:
        # Given
        def handler(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content.decode("utf-8"))
            return _sse_response(
                {
                    "jsonrpc": "2.0",
                    "id": body["id"],
                    "result": {"tools": [{"name": "ping", "description": ""}]},
                }
            )

        client = _make_client(transport=httpx.MockTransport(handler))

        # When
        tools = await client.list_tools(url="https://mcp.example.com/")

        # Then
        assert [t.name for t in tools] == ["ping"]

    async def test_list_tools_raises_handshake_error_on_http_5xx(self) -> None:
        # Given
        def handler(_request: httpx.Request) -> httpx.Response:
            return httpx.Response(status_code=503)

        client = _make_client(transport=httpx.MockTransport(handler))

        # When / Then
        with pytest.raises(McpHandshakeError):
            await client.list_tools(url="https://mcp.example.com/")

    async def test_list_tools_raises_handshake_error_on_json_rpc_error(self) -> None:
        # Given
        def handler(_request: httpx.Request) -> httpx.Response:
            return _json_response(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {"code": -32601, "message": "Method not found"},
                }
            )

        client = _make_client(transport=httpx.MockTransport(handler))

        # When / Then
        with pytest.raises(McpHandshakeError):
            await client.list_tools(url="https://mcp.example.com/")

    async def test_list_tools_re_validates_url(self) -> None:
        # Given
        validator_calls: list[str] = []

        class _RecordingValidator:
            async def validate(self, url: str) -> None:
                validator_calls.append(url)

        def handler(_request: httpx.Request) -> httpx.Response:
            return _json_response({"jsonrpc": "2.0", "id": 1, "result": {"tools": []}})

        client = HttpMcpClient(
            url_safety_validator=_RecordingValidator(),
            http_client_factory=lambda: httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        )

        # When
        await client.list_tools(url="https://mcp.example.com/")

        # Then
        assert validator_calls == ["https://mcp.example.com/"]

    async def test_list_tools_propagates_url_forbidden(self) -> None:
        # Given
        class _RejectingValidator:
            async def validate(self, _url: str) -> None:
                raise McpUrlForbiddenError("forbidden")

        client = HttpMcpClient(
            url_safety_validator=_RejectingValidator(),
            http_client_factory=lambda: httpx.AsyncClient(),
        )

        # When / Then
        with pytest.raises(McpUrlForbiddenError):
            await client.list_tools(url="http://forbidden/")


class TestHttpMcpClientCallTool:
    async def test_call_tool_sends_method_and_arguments(self) -> None:
        # Given
        seen_request: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen_request["body"] = json.loads(request.content.decode("utf-8"))
            return _json_response(
                {
                    "jsonrpc": "2.0",
                    "id": seen_request["body"]["id"],
                    "result": {"content": [{"type": "text", "text": "ok"}], "isError": False},
                }
            )

        client = _make_client(transport=httpx.MockTransport(handler))

        # When
        result = await client.call_tool(
            url="https://mcp.example.com/",
            tool="search",
            arguments={"q": "hello"},
            timeout_seconds=30,
        )

        # Then
        assert seen_request["body"]["method"] == "tools/call"
        assert seen_request["body"]["params"] == {"name": "search", "arguments": {"q": "hello"}}
        assert result["isError"] is False

    async def test_call_tool_translates_timeout(self) -> None:
        # Given
        def handler(_request: httpx.Request) -> httpx.Response:
            raise httpx.ReadTimeout("timeout")

        client = _make_client(transport=httpx.MockTransport(handler))

        # When / Then
        with pytest.raises(McpCallTimeoutError):
            await client.call_tool(
                url="https://mcp.example.com/",
                tool="search",
                arguments={},
                timeout_seconds=1,
            )

    async def test_call_tool_translates_method_not_found_to_tool_not_found(self) -> None:
        # Given
        def handler(_request: httpx.Request) -> httpx.Response:
            return _json_response(
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "error": {"code": -32601, "message": "Tool 'foo' not found"},
                }
            )

        client = _make_client(transport=httpx.MockTransport(handler))

        # When / Then
        with pytest.raises(McpToolNotFoundError):
            await client.call_tool(
                url="https://mcp.example.com/",
                tool="foo",
                arguments={},
                timeout_seconds=30,
            )
