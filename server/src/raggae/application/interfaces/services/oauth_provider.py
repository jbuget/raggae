from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from raggae.application.config.entra_config import EntraConfig


@dataclass
class OAuthUserInfo:
    """User information returned by an OAuth provider after successful authentication."""

    provider_id: str
    email: str
    full_name: str
    provider: str


class OAuthProvider(Protocol):
    """Interface for OAuth 2.0 providers (Entra, Google, GitHub, ...)."""

    async def get_authorization_url(self, state: str, config: "EntraConfig") -> str:
        """Return the provider authorization URL to redirect the user to."""
        ...

    async def exchange_code(self, code: str, state: str, config: "EntraConfig") -> OAuthUserInfo:
        """Exchange an authorization code for user information."""
        ...
