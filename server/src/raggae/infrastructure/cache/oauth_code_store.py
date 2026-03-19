from datetime import UTC, datetime, timedelta

from raggae.application.use_cases.user.handle_oauth_callback import OAuthLoginResult


class InMemoryOAuthCodeStore:
    """Short-lived one-time code store for OAuth post-callback token exchange.

    Maps a UUID code to an OAuthLoginResult with a TTL (default 30s).
    Each code can be consumed exactly once.

    NOTE: Not suitable for multi-instance deployments. Migration path:
    extract this class behind an OAuthCodeStore Protocol and provide
    a Redis-backed implementation.
    """

    def __init__(self) -> None:
        self._codes: dict[str, tuple[OAuthLoginResult, datetime]] = {}

    async def store(self, code: str, result: OAuthLoginResult, ttl_seconds: int = 30) -> None:
        """Store a one-time code associated with an OAuth login result."""
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        self._codes[code] = (result, expires_at)

    async def consume(self, code: str) -> OAuthLoginResult | None:
        """Retrieve and remove the result for a code. Returns None if unknown or expired."""
        entry = self._codes.pop(code, None)
        if entry is None:
            return None
        result, expires_at = entry
        if datetime.now(UTC) >= expires_at:
            return None
        return result
