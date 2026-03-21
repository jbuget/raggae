"""E2E tests for Microsoft Entra SSO endpoints.

Microsoft is fully mocked at the msal.ConfidentialClientApplication level so
no network call is made. The full application stack (routing → use case →
infrastructure → DI) is exercised through httpx.AsyncClient.
"""

from collections.abc import AsyncIterator
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import pytest
from httpx import AsyncClient

from raggae.infrastructure.config.settings import settings


def make_msal_app(
    auth_url: str = "https://login.microsoftonline.com/authorize?foo=bar",
    token_claims: dict | None = None,
) -> MagicMock:
    """Return a mock msal.ConfidentialClientApplication."""
    if token_claims is None:
        token_claims = {
            "oid": "oid-entra-abc",
            "mail": "j.buget@waat.fr",
            "name": "Jérémy Buget",
        }
    app = MagicMock()
    app.get_authorization_request_url.return_value = auth_url
    app.acquire_token_by_authorization_code.return_value = {"id_token_claims": token_claims}
    return app


@pytest.fixture
async def entra_client(client: AsyncClient) -> AsyncIterator[AsyncClient]:
    """Client with Entra SSO enabled and msal mocked."""
    from raggae.presentation.api import dependencies

    with (
        patch.object(settings, "entra_enabled", True),
        patch.object(settings, "entra_client_id", "test-client-id"),
        patch.object(settings, "entra_client_secret", "test-secret"),
        patch.object(settings, "entra_tenant_id", "test-tenant"),
        patch.object(settings, "entra_redirect_uri", "https://test.example.com/callback"),
        patch.object(settings, "entra_allowed_domains", ["waat.fr"]),
        patch.object(settings, "frontend_url", "http://localhost:3000"),
    ):
        dependencies._oauth_code_store._codes.clear()
        yield client


async def _do_login(client: AsyncClient, mock_app: MagicMock) -> tuple[str, str]:
    """Perform the /login step and return (csrf_token, raw_cookie_value)."""
    with patch(
        "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
        return_value=mock_app,
    ):
        resp = await client.get(
            "/api/v1/auth/entra/login",
            params={"redirect_url": "/projects/42"},
            follow_redirects=False,
        )
    assert resp.status_code == 302
    csrf_token: str = mock_app.get_authorization_request_url.call_args.kwargs["state"]
    raw_cookie: str = resp.cookies["oauth_state"]
    return csrf_token, raw_cookie


async def _do_callback(
    client: AsyncClient,
    mock_app: MagicMock,
    csrf_token: str,
    raw_cookie: str,
) -> str:
    """Perform the /callback step and return the one-time code."""
    with patch(
        "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
        return_value=mock_app,
    ):
        resp = await client.get(
            "/api/v1/auth/entra/callback",
            params={"code": "auth-code", "state": csrf_token},
            cookies={"oauth_state": raw_cookie},
            follow_redirects=False,
        )
    assert resp.status_code == 302
    location = resp.headers["location"]
    return parse_qs(urlparse(location).query)["code"][0]


class TestEntraLoginEndpoint:
    async def test_e2e_entra_login_returns_501_when_disabled(self, client: AsyncClient) -> None:
        # When — ENTRA_ENABLED=false (explicitly disabled)
        with patch.object(settings, "entra_enabled", False):
            resp = await client.get("/api/v1/auth/entra/login", follow_redirects=False)

        # Then
        assert resp.status_code == 501

    async def test_e2e_entra_login_redirects_to_microsoft(self, entra_client: AsyncClient) -> None:
        # Given
        mock_app = make_msal_app()

        # When
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            resp = await entra_client.get("/api/v1/auth/entra/login", follow_redirects=False)

        # Then
        assert resp.status_code == 302
        assert resp.headers["location"].startswith("https://login.microsoftonline.com/authorize")

    async def test_e2e_entra_login_sets_oauth_state_cookie(self, entra_client: AsyncClient) -> None:
        # Given
        mock_app = make_msal_app()

        # When
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            resp = await entra_client.get("/api/v1/auth/entra/login", follow_redirects=False)

        # Then — signed state cookie present
        assert "oauth_state" in resp.cookies
        assert len(resp.cookies["oauth_state"]) > 0


class TestEntraCallbackEndpoint:
    async def test_e2e_entra_callback_returns_400_on_state_mismatch(self, entra_client: AsyncClient) -> None:
        # Given — perform login to get a valid cookie
        mock_app = make_msal_app()
        _, raw_cookie = await _do_login(entra_client, mock_app)

        # When — send a wrong state value
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            resp = await entra_client.get(
                "/api/v1/auth/entra/callback",
                params={"code": "auth-code", "state": "WRONG-STATE"},
                cookies={"oauth_state": raw_cookie},
                follow_redirects=False,
            )

        # Then
        assert resp.status_code == 400

    async def test_e2e_entra_callback_returns_400_without_cookie(self, entra_client: AsyncClient) -> None:
        # When — no state cookie at all
        resp = await entra_client.get(
            "/api/v1/auth/entra/callback",
            params={"code": "auth-code", "state": "any-state"},
            follow_redirects=False,
        )

        # Then
        assert resp.status_code == 400

    async def test_e2e_entra_callback_returns_403_when_domain_not_allowed(
        self, entra_client: AsyncClient
    ) -> None:
        # Given — login ok, but token returns a non-allowed domain
        mock_app = make_msal_app(
            token_claims={
                "oid": "oid-pix",
                "mail": "j.buget@pix.fr",
                "name": "Jérémy Buget",
            }
        )
        csrf_token, raw_cookie = await _do_login(entra_client, mock_app)

        # When
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            resp = await entra_client.get(
                "/api/v1/auth/entra/callback",
                params={"code": "auth-code", "state": csrf_token},
                cookies={"oauth_state": raw_cookie},
                follow_redirects=False,
            )

        # Then
        assert resp.status_code == 403

    async def test_e2e_entra_callback_redirects_to_frontend_on_success(
        self, entra_client: AsyncClient
    ) -> None:
        # Given
        mock_app = make_msal_app()
        csrf_token, raw_cookie = await _do_login(entra_client, mock_app)

        # When
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            resp = await entra_client.get(
                "/api/v1/auth/entra/callback",
                params={"code": "auth-code", "state": csrf_token},
                cookies={"oauth_state": raw_cookie},
                follow_redirects=False,
            )

        # Then
        assert resp.status_code == 302
        assert resp.headers["location"].startswith("http://localhost:3000/auth/callback")
        assert "code=" in resp.headers["location"]

    async def test_e2e_entra_callback_clears_oauth_state_cookie(self, entra_client: AsyncClient) -> None:
        # Given
        mock_app = make_msal_app()
        csrf_token, raw_cookie = await _do_login(entra_client, mock_app)

        # When
        with patch(
            "raggae.infrastructure.services.entra_oauth_provider.msal.ConfidentialClientApplication",
            return_value=mock_app,
        ):
            resp = await entra_client.get(
                "/api/v1/auth/entra/callback",
                params={"code": "auth-code", "state": csrf_token},
                cookies={"oauth_state": raw_cookie},
                follow_redirects=False,
            )

        # Then — cookie deleted (empty value or Max-Age=0)
        assert resp.status_code == 302
        set_cookie = resp.headers.get("set-cookie", "")
        assert "oauth_state" in set_cookie


class TestEntraTokenEndpoint:
    async def test_e2e_entra_token_returns_501_when_disabled(self, client: AsyncClient) -> None:
        # When — ENTRA_ENABLED=false (explicitly disabled)
        with patch.object(settings, "entra_enabled", False):
            resp = await client.post("/api/v1/auth/entra/token", json={"code": "any"})

        # Then
        assert resp.status_code == 501

    async def test_e2e_entra_token_returns_400_for_invalid_code(self, entra_client: AsyncClient) -> None:
        # When
        resp = await entra_client.post("/api/v1/auth/entra/token", json={"code": "invalid-code"})

        # Then
        assert resp.status_code == 400

    async def test_e2e_entra_token_returns_400_on_code_reuse(self, entra_client: AsyncClient) -> None:
        # Given — full flow to get a valid code
        mock_app = make_msal_app()
        csrf_token, raw_cookie = await _do_login(entra_client, mock_app)
        one_time_code = await _do_callback(entra_client, mock_app, csrf_token, raw_cookie)

        # First use — ok
        await entra_client.post("/api/v1/auth/entra/token", json={"code": one_time_code})

        # When — second use
        resp = await entra_client.post("/api/v1/auth/entra/token", json={"code": one_time_code})

        # Then
        assert resp.status_code == 400


class TestEntraFullFlow:
    async def test_e2e_full_sso_flow_creates_new_user(self, entra_client: AsyncClient) -> None:
        # Given
        mock_app = make_msal_app()
        csrf_token, raw_cookie = await _do_login(entra_client, mock_app)
        one_time_code = await _do_callback(entra_client, mock_app, csrf_token, raw_cookie)

        # When — exchange one-time code
        resp = await entra_client.post("/api/v1/auth/entra/token", json={"code": one_time_code})

        # Then
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_new_user"] is True
        assert data["account_linked"] is False
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    async def test_e2e_full_sso_flow_links_existing_local_account(self, entra_client: AsyncClient) -> None:
        # Given — pre-existing local account with same email
        await entra_client.post(
            "/api/v1/auth/register",
            json={
                "email": "j.buget@waat.fr",
                "password": "SecurePass123!",
                "full_name": "Jérémy Buget",
            },
        )

        # When — SSO flow for same email
        mock_app = make_msal_app()
        csrf_token, raw_cookie = await _do_login(entra_client, mock_app)
        one_time_code = await _do_callback(entra_client, mock_app, csrf_token, raw_cookie)
        resp = await entra_client.post("/api/v1/auth/entra/token", json={"code": one_time_code})

        # Then
        assert resp.status_code == 200
        data = resp.json()
        assert data["account_linked"] is True
        assert data["is_new_user"] is False
        assert len(data["access_token"]) > 0

    async def test_e2e_full_sso_flow_jwt_grants_access_to_protected_endpoint(
        self, entra_client: AsyncClient
    ) -> None:
        # Given — full SSO flow
        mock_app = make_msal_app()
        csrf_token, raw_cookie = await _do_login(entra_client, mock_app)
        one_time_code = await _do_callback(entra_client, mock_app, csrf_token, raw_cookie)
        token_resp = await entra_client.post("/api/v1/auth/entra/token", json={"code": one_time_code})
        access_token = token_resp.json()["access_token"]

        # When — use JWT to call a protected endpoint
        me_resp = await entra_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        # Then
        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["email"] == "j.buget@waat.fr"
        assert data["full_name"] == "Jérémy Buget"

    async def test_e2e_second_sso_login_recognises_existing_entra_account(
        self, entra_client: AsyncClient
    ) -> None:
        # Given — first SSO login creates the account
        mock_app = make_msal_app()
        csrf_token, raw_cookie = await _do_login(entra_client, mock_app)
        code = await _do_callback(entra_client, mock_app, csrf_token, raw_cookie)
        await entra_client.post("/api/v1/auth/entra/token", json={"code": code})

        # When — second login with same oid
        csrf_token2, raw_cookie2 = await _do_login(entra_client, mock_app)
        code2 = await _do_callback(entra_client, mock_app, csrf_token2, raw_cookie2)
        resp = await entra_client.post("/api/v1/auth/entra/token", json={"code": code2})

        # Then — recognised, not a new user
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_new_user"] is False
        assert data["account_linked"] is False
