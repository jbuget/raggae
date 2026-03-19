from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass
class OAuthState:
    """OAuth 2.0 state parameter payload.

    Carries CSRF token, post-auth redirect URL and expiry.
    Signed and stored as a short-lived cookie by the presentation layer.
    """

    csrf_token: str
    redirect_url: str
    expires_at: datetime

    def is_expired(self) -> bool:
        """Return True if the state has passed its expiry time."""
        return datetime.now(UTC) >= self.expires_at
