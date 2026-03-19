from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from raggae.application.config.entra_config import EntraConfig
from raggae.application.dto.oauth_state import OAuthState
from raggae.application.use_cases.user.initiate_oauth_login import InitiateOAuthLogin


@pytest.fixture
def entra_config() -> EntraConfig:
    return EntraConfig(
        client_id="client-id",
        client_secret="client-secret",
        tenant_id="tenant-id",
        redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
        allowed_domains=["waat.fr"],
    )


@pytest.fixture
def mock_oauth_provider() -> AsyncMock:
    provider = AsyncMock()
    provider.get_authorization_url.return_value = "https://login.microsoftonline.com/authorize"
    return provider


@pytest.fixture
def use_case(mock_oauth_provider: AsyncMock, entra_config: EntraConfig) -> InitiateOAuthLogin:
    return InitiateOAuthLogin(oauth_provider=mock_oauth_provider, config=entra_config)


class TestOAuthState:
    def test_create_oauth_state_with_all_fields(self) -> None:
        # Given
        expires_at = datetime.now(UTC) + timedelta(minutes=5)

        # When
        state = OAuthState(
            csrf_token="token-abc",
            redirect_url="/projects/42",
            expires_at=expires_at,
        )

        # Then
        assert state.csrf_token == "token-abc"
        assert state.redirect_url == "/projects/42"
        assert state.expires_at == expires_at

    def test_is_expired_returns_false_for_future_state(self) -> None:
        # Given
        state = OAuthState(
            csrf_token="token-abc",
            redirect_url="/",
            expires_at=datetime.now(UTC) + timedelta(minutes=5),
        )

        # When / Then
        assert state.is_expired() is False

    def test_is_expired_returns_true_for_past_state(self) -> None:
        # Given
        state = OAuthState(
            csrf_token="token-abc",
            redirect_url="/",
            expires_at=datetime.now(UTC) - timedelta(seconds=1),
        )

        # When / Then
        assert state.is_expired() is True


class TestInitiateOAuthLogin:
    async def test_execute_returns_authorization_url(
        self,
        use_case: InitiateOAuthLogin,
        mock_oauth_provider: AsyncMock,
    ) -> None:
        # When
        result = await use_case.execute(redirect_url="/")

        # Then
        assert result.authorization_url == "https://login.microsoftonline.com/authorize"
        mock_oauth_provider.get_authorization_url.assert_called_once()

    async def test_execute_returns_state_with_redirect_url(
        self,
        use_case: InitiateOAuthLogin,
    ) -> None:
        # When
        result = await use_case.execute(redirect_url="/projects/42")

        # Then
        assert result.state.redirect_url == "/projects/42"

    async def test_execute_uses_slash_as_default_redirect_url(
        self,
        use_case: InitiateOAuthLogin,
    ) -> None:
        # When
        result = await use_case.execute()

        # Then
        assert result.state.redirect_url == "/"

    async def test_execute_state_has_csrf_token(
        self,
        use_case: InitiateOAuthLogin,
    ) -> None:
        # When
        result = await use_case.execute()

        # Then
        assert result.state.csrf_token
        assert len(result.state.csrf_token) > 0

    async def test_execute_generates_unique_csrf_token_each_time(
        self,
        use_case: InitiateOAuthLogin,
    ) -> None:
        # When
        result_a = await use_case.execute()
        result_b = await use_case.execute()

        # Then
        assert result_a.state.csrf_token != result_b.state.csrf_token

    async def test_execute_state_expires_in_five_minutes(
        self,
        use_case: InitiateOAuthLogin,
    ) -> None:
        # When
        before = datetime.now(UTC)
        result = await use_case.execute()
        after = datetime.now(UTC)

        # Then
        expected_min = before + timedelta(minutes=5)
        expected_max = after + timedelta(minutes=5)
        assert expected_min <= result.state.expires_at <= expected_max

    async def test_execute_passes_csrf_token_as_state_to_provider(
        self,
        use_case: InitiateOAuthLogin,
        mock_oauth_provider: AsyncMock,
        entra_config: EntraConfig,
    ) -> None:
        # When
        result = await use_case.execute()

        # Then — the provider receives the csrf_token as the state string
        mock_oauth_provider.get_authorization_url.assert_called_once_with(
            state=result.state.csrf_token,
            config=entra_config,
        )
