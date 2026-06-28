from typing import Protocol


class UrlSafetyValidator(Protocol):
    """Validates an outbound URL against SSRF and scheme rules.

    Implementations must enforce HTTPS, resolve the host via DNS, and refuse loopback,
    link-local, private, or otherwise reserved IP ranges.
    """

    async def validate(self, url: str) -> None:
        """Raises `McpUrlForbiddenError` when the URL is unsafe."""
        ...
