from typing import Any, Protocol

from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot


class McpClient(Protocol):
    """Outbound MCP transport client (HTTP/SSE).

    Implementations must re-validate URLs against an `UrlSafetyValidator` before every call.
    """

    async def list_tools(
        self,
        url: str,
        bearer_token: str | None = None,
    ) -> list[McpToolSnapshot]:
        """Call `tools/list` on the remote MCP server and return the snapshot.

        Raises `McpHandshakeError` if the call fails.
        Raises `McpUrlForbiddenError` if the URL is rejected by the safety validator.
        """
        ...

    async def call_tool(
        self,
        url: str,
        tool: str,
        arguments: dict[str, Any],
        timeout_seconds: int,
        bearer_token: str | None = None,
    ) -> dict[str, Any]:
        """Invoke one tool on the remote MCP server and return its result payload.

        Raises `McpCallTimeoutError` on timeout, `McpToolNotFoundError` if tool is unknown,
        and `McpUrlForbiddenError` if the URL is rejected by the safety validator.
        """
        ...
