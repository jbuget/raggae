"""Tests anti-SSRF du UrlSafetyValidatorImpl.

Couverture exhaustive des familles d'IP refusées :
- IPv4 loopback (127/8), private (10/8, 172.16/12, 192.168/16),
  link-local (169.254/16), multicast, broadcast.
- IPv6 loopback (::1), link-local (fe80::/10), unique-local (fc00::/7).
"""

import pytest

from raggae.domain.exceptions.mcp_exceptions import McpUrlForbiddenError
from raggae.infrastructure.services.url_safety_validator_impl import (
    UrlSafetyValidatorImpl,
)


class _StaticResolver:
    def __init__(self, addresses: list[str]) -> None:
        self._addresses = addresses

    async def __call__(self, _host: str) -> list[str]:
        return self._addresses


class TestUrlSafetyValidatorImpl:
    async def test_accepts_public_https_host(self) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver(["93.184.216.34"]))

        await validator.validate("https://example.com/mcp")

    async def test_rejects_http_scheme(self) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver(["93.184.216.34"]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("http://example.com/mcp")

    async def test_rejects_scheme_other_than_http_https(self) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver(["93.184.216.34"]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("ftp://example.com/mcp")

    async def test_rejects_url_without_host(self) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver([]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("https:///path-only")

    async def test_rejects_malformed_url(self) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver([]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("not a url")

    @pytest.mark.parametrize(
        "ip",
        [
            "127.0.0.1",
            "127.0.0.5",
            "127.255.255.255",
            "10.0.0.1",
            "10.255.0.5",
            "172.16.0.1",
            "172.31.255.254",
            "192.168.1.1",
            "169.254.169.254",
            "224.0.0.1",
            "255.255.255.255",
            "0.0.0.0",
        ],
    )
    async def test_rejects_ipv4_forbidden_ranges(self, ip: str) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver([ip]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("https://internal.example/mcp")

    @pytest.mark.parametrize(
        "ip",
        [
            "::1",
            "fe80::1",
            "fe80::abcd:1234",
            "fc00::1",
            "fd12:3456:789a::1",
            "ff02::1",
        ],
    )
    async def test_rejects_ipv6_forbidden_ranges(self, ip: str) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver([ip]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("https://internal.example/mcp")

    async def test_rejects_when_any_resolved_ip_is_forbidden(self) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver(["93.184.216.34", "10.0.0.5"]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("https://mixed.example/mcp")

    async def test_rejects_literal_ipv4_in_host(self) -> None:
        # Avec un literal IP dans l'URL, le validator doit aussi détecter le risque.
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver(["127.0.0.1"]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("https://127.0.0.1/mcp")

    async def test_accepts_when_all_resolved_ips_are_public(self) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver(["93.184.216.34", "2606:2800:220:1::1"]))

        await validator.validate("https://mcp.example.com/")

    async def test_rejects_when_dns_returns_no_address(self) -> None:
        validator = UrlSafetyValidatorImpl(resolver=_StaticResolver([]))

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("https://unknown.example/")

    async def test_rejects_when_resolver_raises(self) -> None:
        async def _failing(_host: str) -> list[str]:
            raise OSError("DNS failure")

        validator = UrlSafetyValidatorImpl(resolver=_failing)

        with pytest.raises(McpUrlForbiddenError):
            await validator.validate("https://broken.example/")
