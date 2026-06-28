"""Executes one MCP tool call given its descriptor.

The executor owns the bearer-token decryption flow so callers don't need to know
how secrets are stored; they only pass an `McpToolDescriptor`. This service is
the bridge between a future chat tool-calling loop and the `McpClient` port.
"""

import logging
from time import perf_counter
from typing import Any
from uuid import UUID

from raggae.application.interfaces.repositories.org_mcp_server_repository import (
    OrgMcpServerRepository,
)
from raggae.application.interfaces.services.mcp_bearer_token_crypto_service import (
    McpBearerTokenCryptoService,
)
from raggae.application.interfaces.services.mcp_client import McpClient
from raggae.domain.exceptions.mcp_exceptions import McpServerNotFoundError
from raggae.domain.value_objects.mcp_tool_descriptor import McpToolDescriptor

logger = logging.getLogger(__name__)


class McpToolExecutor:
    """Application service: invoke one MCP tool by its prefixed name."""

    def __init__(
        self,
        org_mcp_server_repository: OrgMcpServerRepository,
        mcp_client: McpClient,
        bearer_token_crypto_service: McpBearerTokenCryptoService,
    ) -> None:
        self._server_repository = org_mcp_server_repository
        self._mcp_client = mcp_client
        self._crypto = bearer_token_crypto_service

    async def execute(
        self,
        descriptor: McpToolDescriptor,
        arguments: dict[str, Any],
        organization_id: UUID,
    ) -> dict[str, Any]:
        bearer_token: str | None = None
        if descriptor.has_bearer_token:
            server = await self._server_repository.find_by_id(descriptor.mcp_server_id, organization_id)
            if server is None:
                raise McpServerNotFoundError(f"MCP server {descriptor.mcp_server_id} not found")
            if server.encrypted_bearer_token is not None:
                bearer_token = self._crypto.decrypt(server.encrypted_bearer_token)

        started_at = perf_counter()
        log_extra = {
            "mcp_server_id": str(descriptor.mcp_server_id),
            "mcp_server_slug": descriptor.mcp_server_slug,
            "tool_name": descriptor.original_name,
        }
        try:
            result = await self._mcp_client.call_tool(
                url=descriptor.server_url,
                tool=descriptor.original_name,
                arguments=arguments,
                timeout_seconds=descriptor.timeout_seconds,
                bearer_token=bearer_token,
            )
        except Exception:
            elapsed_ms = (perf_counter() - started_at) * 1000.0
            logger.exception(
                "mcp_tool_call_failed",
                extra={**log_extra, "elapsed_ms": round(elapsed_ms, 2)},
            )
            raise
        elapsed_ms = (perf_counter() - started_at) * 1000.0
        logger.info(
            "mcp_tool_call_succeeded",
            extra={**log_extra, "elapsed_ms": round(elapsed_ms, 2)},
        )
        return result
