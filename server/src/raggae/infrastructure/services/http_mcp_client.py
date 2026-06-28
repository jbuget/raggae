"""HTTP/SSE client implementing the MCP `Streamable HTTP` transport.

JSON-RPC 2.0 envelopes are POSTed to the MCP server endpoint. The server may
respond with `application/json` (single response) or `text/event-stream`
(SSE events containing JSON-RPC payloads). Both are supported.
"""

import itertools
import json
from collections.abc import Callable
from typing import Any

import httpx

from raggae.application.interfaces.services.url_safety_validator import UrlSafetyValidator
from raggae.domain.exceptions.mcp_exceptions import (
    McpCallTimeoutError,
    McpHandshakeError,
    McpToolNotFoundError,
)
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot

_MCP_PROTOCOL_VERSION = "2025-06-18"
_JSON_RPC_METHOD_NOT_FOUND = -32601
_JSON_RPC_INVALID_PARAMS = -32602

HttpClientFactory = Callable[[], httpx.AsyncClient]


class HttpMcpClient:
    """MCP client using `httpx` over HTTPS."""

    def __init__(
        self,
        url_safety_validator: UrlSafetyValidator,
        http_client_factory: HttpClientFactory | None = None,
    ) -> None:
        self._url_safety_validator = url_safety_validator
        self._http_client_factory = http_client_factory or (lambda: httpx.AsyncClient())
        self._id_counter = itertools.count(1)

    async def list_tools(
        self,
        url: str,
        bearer_token: str | None = None,
    ) -> list[McpToolSnapshot]:
        await self._url_safety_validator.validate(url)
        try:
            result = await self._call_jsonrpc(
                url=url,
                method="tools/list",
                params={},
                bearer_token=bearer_token,
                timeout_seconds=30,
            )
        except McpToolNotFoundError as exc:
            raise McpHandshakeError(str(exc)) from exc
        return _parse_tools(result)

    async def call_tool(
        self,
        url: str,
        tool: str,
        arguments: dict[str, Any],
        timeout_seconds: int,
        bearer_token: str | None = None,
    ) -> dict[str, Any]:
        await self._url_safety_validator.validate(url)
        return await self._call_jsonrpc(
            url=url,
            method="tools/call",
            params={"name": tool, "arguments": arguments},
            bearer_token=bearer_token,
            timeout_seconds=timeout_seconds,
        )

    async def _call_jsonrpc(
        self,
        *,
        url: str,
        method: str,
        params: dict[str, Any],
        bearer_token: str | None,
        timeout_seconds: int,
    ) -> dict[str, Any]:
        request_id = next(self._id_counter)
        payload = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": _MCP_PROTOCOL_VERSION,
        }
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        try:
            async with self._http_client_factory() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=timeout_seconds,
                )
        except (httpx.TimeoutException, TimeoutError) as exc:
            raise McpCallTimeoutError(f"MCP call '{method}' timed out after {timeout_seconds}s") from exc

        if response.status_code >= 500:
            raise McpHandshakeError(f"MCP server returned HTTP {response.status_code}")
        if response.status_code >= 400:
            raise McpHandshakeError(f"MCP server rejected request: HTTP {response.status_code}")

        envelope = _parse_envelope(response, expected_id=request_id)
        if "error" in envelope:
            _raise_error(method, envelope["error"])
        result = envelope.get("result")
        if not isinstance(result, dict):
            raise McpHandshakeError(f"MCP server returned no result for '{method}'")
        return result


def _parse_envelope(response: httpx.Response, expected_id: int) -> dict[str, Any]:
    content_type = response.headers.get("content-type", "").lower()
    if "text/event-stream" in content_type:
        payload = _parse_sse(response.text, expected_id)
    else:
        try:
            payload = response.json()
        except json.JSONDecodeError as exc:
            raise McpHandshakeError(f"MCP server returned non-JSON body: {exc}") from exc
    if not isinstance(payload, dict):
        raise McpHandshakeError("MCP server returned a non-object JSON-RPC envelope")
    return payload


def _parse_sse(body: str, expected_id: int) -> dict[str, Any]:
    for block in body.split("\n\n"):
        data_lines = [line[len("data:") :].strip() for line in block.splitlines() if line.startswith("data:")]
        if not data_lines:
            continue
        try:
            payload = json.loads("\n".join(data_lines))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict) and payload.get("id") == expected_id:
            return payload
    raise McpHandshakeError("MCP SSE response did not contain a matching JSON-RPC payload")


def _raise_error(method: str, error: dict[str, Any]) -> None:
    code = error.get("code")
    message = str(error.get("message", "unknown error"))
    if method == "tools/call" and code in (_JSON_RPC_METHOD_NOT_FOUND, _JSON_RPC_INVALID_PARAMS):
        raise McpToolNotFoundError(message)
    raise McpHandshakeError(f"MCP JSON-RPC error {code}: {message}")


def _parse_tools(result: dict[str, Any]) -> list[McpToolSnapshot]:
    raw_tools = result.get("tools") or []
    if not isinstance(raw_tools, list):
        raise McpHandshakeError("Invalid 'tools' field in tools/list response")
    snapshots: list[McpToolSnapshot] = []
    for raw in raw_tools:
        if not isinstance(raw, dict) or "name" not in raw:
            continue
        schema = raw.get("inputSchema") or raw.get("input_schema") or {}
        snapshots.append(
            McpToolSnapshot(
                name=str(raw["name"]),
                description=str(raw.get("description", "")),
                input_schema=dict(schema) if isinstance(schema, dict) else {},
            )
        )
    return snapshots
