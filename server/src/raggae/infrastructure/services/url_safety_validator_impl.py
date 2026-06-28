import asyncio
import ipaddress
import socket
from collections.abc import Awaitable, Callable
from urllib.parse import urlparse

from raggae.domain.exceptions.mcp_exceptions import McpUrlForbiddenError

DnsResolver = Callable[[str], Awaitable[list[str]]]


async def _resolve_host(host: str) -> list[str]:
    """Default async resolver: resolves a hostname to all its A/AAAA records."""
    loop = asyncio.get_running_loop()
    infos = await loop.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    return [info[4][0] for info in infos]


class UrlSafetyValidatorImpl:
    """Validates outbound URLs against SSRF: HTTPS-only + denylist of private/reserved IPs."""

    def __init__(self, resolver: DnsResolver | None = None) -> None:
        self._resolver = resolver or _resolve_host

    async def validate(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https":
            raise McpUrlForbiddenError(f"URL scheme must be https, got '{parsed.scheme}'")
        host = parsed.hostname
        if not host:
            raise McpUrlForbiddenError("URL must include a hostname")

        try:
            addresses = await self._resolver(host)
        except (OSError, McpUrlForbiddenError) as exc:
            raise McpUrlForbiddenError(f"Cannot resolve host '{host}': {exc}") from exc

        if not addresses:
            raise McpUrlForbiddenError(f"Host '{host}' resolved to no address")

        for raw in addresses:
            try:
                address = ipaddress.ip_address(raw)
            except ValueError as exc:
                raise McpUrlForbiddenError(f"Invalid IP address '{raw}' for host '{host}'") from exc
            if _is_forbidden(address):
                raise McpUrlForbiddenError(f"Host '{host}' resolves to forbidden address '{raw}'")


def _is_forbidden(address: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        address.is_loopback
        or address.is_link_local
        or address.is_private
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    )
