from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from raggae.application.config.entra_config import EntraConfig
from raggae.application.dto.oauth_state import OAuthState
from raggae.application.interfaces.services.oauth_provider import OAuthProvider

_STATE_TTL_MINUTES = 5


@dataclass
class InitiateOAuthLoginResult:
    """Result of initiating an OAuth login flow."""

    authorization_url: str
    state: OAuthState


class InitiateOAuthLogin:
    """Use Case: Start an OAuth Authorization Code flow.

    Generates a signed CSRF state and returns the provider authorization URL.
    The state is returned to the presentation layer for cookie storage.
    """

    def __init__(self, oauth_provider: OAuthProvider, config: EntraConfig) -> None:
        self._oauth_provider = oauth_provider
        self._config = config

    async def execute(self, redirect_url: str = "/") -> InitiateOAuthLoginResult:
        state = OAuthState(
            csrf_token=str(uuid4()),
            redirect_url=redirect_url,
            expires_at=datetime.now(UTC) + timedelta(minutes=_STATE_TTL_MINUTES),
        )
        authorization_url = await self._oauth_provider.get_authorization_url(
            state=state.csrf_token,
            config=self._config,
        )
        return InitiateOAuthLoginResult(authorization_url=authorization_url, state=state)
