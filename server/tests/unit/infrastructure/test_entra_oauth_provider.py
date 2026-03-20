from unittest.mock import MagicMock, patch

import pytest

from raggae.application.config.entra_config import EntraConfig
from raggae.domain.exceptions.user_exceptions import OAuthProviderError
from raggae.infrastructure.services.entra_oauth_provider import EntraOAuthProvider

AUTHORITY = "https://login.microsoftonline.com/tenant-id"
SCOPES = ["openid", "profile", "email", "User.Read"]


@pytest.fixture
def config() -> EntraConfig:
    return EntraConfig(
        client_id="client-id",
        client_secret="client-secret",
        tenant_id="tenant-id",
        redirect_uri="https://app.example.com/callback",
        allowed_domains=["waat.fr"],
    )


@pytest.fixture
def provider() -> EntraOAuthProvider:
    return EntraOAuthProvider()


def make_msal_app(auth_url: str = "https://login.microsoftonline.com/authorize") -> MagicMock:
    app = MagicMock()
    app.get_authorization_request_url.return_value = auth_url
    return app


def make_token_result(claims: dict) -> dict:
    return {"id_token_claims": claims}


def make_claims(
    oid: str = "oid-abc-123",
    mail: str | None = "j.buget@waat.fr",
    preferred_username: str | None = None,
    upn: str | None = None,
    display_name: str | None = "Jérémy Buget",
    given_name: str | None = None,
    surname: str | None = None,
) -> dict:
    claims: dict = {"oid": oid}
    if mail is not None:
        claims["mail"] = mail
    if preferred_username is not None:
        claims["preferred_username"] = preferred_username
    if upn is not None:
        claims["upn"] = upn
    if display_name is not None:
        claims["name"] = display_name
    if given_name is not None:
        claims["given_name"] = given_name
    if surname is not None:
        claims["family_name"] = surname
    return claims


class TestEntraOAuthProviderGetAuthorizationUrl:
    async def test_returns_authorization_url_from_msal(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given
        mock_app = make_msal_app("https://login.microsoftonline.com/authorize?foo=bar")
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            # When
            url = await provider.get_authorization_url(state="csrf-token", config=config)

        # Then
        assert url == "https://login.microsoftonline.com/authorize?foo=bar"

    async def test_builds_msal_app_with_correct_authority(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given
        mock_app = make_msal_app()
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication"
        ) as mock_cls:
            mock_cls.return_value = mock_app

            # When
            await provider.get_authorization_url(state="csrf-token", config=config)

        # Then
        mock_cls.assert_called_once_with(
            client_id="client-id",
            client_credential="client-secret",
            authority=AUTHORITY,
        )

    async def test_passes_scopes_and_redirect_uri_to_msal(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given
        mock_app = make_msal_app()
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            # When
            await provider.get_authorization_url(state="csrf-token", config=config)

        # Then
        call_kwargs = mock_app.get_authorization_request_url.call_args
        assert call_kwargs.kwargs["scopes"] == SCOPES
        assert call_kwargs.kwargs["redirect_uri"] == config.redirect_uri
        assert call_kwargs.kwargs["state"] == "csrf-token"

    async def test_includes_pkce_code_challenge_in_request(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given
        mock_app = make_msal_app()
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            # When
            await provider.get_authorization_url(state="csrf-token", config=config)

        # Then — PKCE challenge present and method is S256
        call_kwargs = mock_app.get_authorization_request_url.call_args.kwargs
        assert "code_challenge" in call_kwargs
        assert call_kwargs["code_challenge_method"] == "S256"
        assert len(call_kwargs["code_challenge"]) > 0


class TestEntraOAuthProviderExchangeCode:
    async def test_returns_oauth_user_info_with_oid_as_provider_id(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given — initiate first to store PKCE verifier
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = make_token_result(make_claims())
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)
            result = await provider.exchange_code(code="auth-code", state="csrf-token", config=config)

        # Then
        assert result.provider_id == "oid-abc-123"
        assert result.provider == "entra"

    async def test_email_resolved_from_mail_claim(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = make_token_result(
            make_claims(mail="mail@waat.fr", preferred_username="pref@waat.fr")
        )
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)
            result = await provider.exchange_code(code="auth-code", state="csrf-token", config=config)

        # Then — mail takes priority
        assert result.email == "mail@waat.fr"

    async def test_email_falls_back_to_preferred_username(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given — no mail claim
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = make_token_result(
            make_claims(mail=None, preferred_username="pref@waat.fr", upn="upn@waat.fr")
        )
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)
            result = await provider.exchange_code(code="auth-code", state="csrf-token", config=config)

        assert result.email == "pref@waat.fr"

    async def test_email_falls_back_to_upn(self, provider: EntraOAuthProvider, config: EntraConfig) -> None:
        # Given — no mail, no preferred_username
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = make_token_result(
            make_claims(mail=None, preferred_username=None, upn="upn@waat.fr")
        )
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)
            result = await provider.exchange_code(code="auth-code", state="csrf-token", config=config)

        assert result.email == "upn@waat.fr"

    async def test_full_name_resolved_from_given_name_and_surname(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = make_token_result(
            make_claims(given_name="Jérémy", surname="Buget", display_name="Jérémy Buget")
        )
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)
            result = await provider.exchange_code(code="auth-code", state="csrf-token", config=config)

        assert result.full_name == "Jérémy Buget"

    async def test_full_name_falls_back_to_display_name(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given — no given_name / surname
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = make_token_result(
            make_claims(given_name=None, surname=None, display_name="Jérémy Buget")
        )
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)
            result = await provider.exchange_code(code="auth-code", state="csrf-token", config=config)

        assert result.full_name == "Jérémy Buget"

    async def test_full_name_falls_back_to_local_email_part(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given — no name claims at all
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = make_token_result(
            make_claims(given_name=None, surname=None, display_name=None)
        )
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)
            result = await provider.exchange_code(code="auth-code", state="csrf-token", config=config)

        assert result.full_name == "j.buget"

    async def test_exchange_code_raises_oauth_provider_error_on_msal_error(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = {
            "error": "invalid_grant",
            "error_description": "Code expired",
        }
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)

            # When / Then
            with pytest.raises(OAuthProviderError):
                await provider.exchange_code(code="bad-code", state="csrf-token", config=config)

    async def test_exchange_code_passes_pkce_verifier_to_msal(
        self, provider: EntraOAuthProvider, config: EntraConfig
    ) -> None:
        # Given
        mock_app = make_msal_app()
        mock_app.acquire_token_by_authorization_code.return_value = make_token_result(make_claims())
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            await provider.get_authorization_url(state="csrf-token", config=config)
            await provider.exchange_code(code="auth-code", state="csrf-token", config=config)

        # Then — code_verifier passed to MSAL token request
        call_kwargs = mock_app.acquire_token_by_authorization_code.call_args.kwargs
        assert "code_verifier" in call_kwargs
        assert len(call_kwargs["code_verifier"]) > 0
