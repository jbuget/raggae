import asyncio
import logging

import msal

from raggae.application.config.entra_config import EntraConfig
from raggae.application.interfaces.services.oauth_provider import OAuthUserInfo
from raggae.domain.exceptions.user_exceptions import OAuthProviderError

logger = logging.getLogger(__name__)

_SCOPES = ["User.Read"]


def _resolve_email(claims: dict[str, object]) -> str:
    for key in ("mail", "preferred_username", "upn"):
        value = claims.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def _resolve_full_name(claims: dict[str, object], email: str) -> str:
    given_name = str(claims.get("given_name") or "").strip()
    surname = str(claims.get("family_name") or "").strip()
    if given_name and surname:
        return f"{given_name} {surname}"
    display_name = str(claims.get("name") or "").strip()
    if display_name:
        return display_name
    return email.split("@")[0]


class EntraOAuthProvider:
    """OAuth 2.0 provider implementation for Microsoft Entra ID.

    Uses MSAL (Microsoft Authentication Library) for token acquisition
    and validation. PKCE is handled internally by MSAL via
    initiate_auth_code_flow / acquire_token_by_auth_code_flow.
    The auth_code_flow dict is stored in-memory keyed by the CSRF token
    for retrieval during code exchange.

    NOTE: The in-memory flow store is not suitable for multi-instance
    deployments. Migration path: extract _flow_store behind a Protocol
    and provide a Redis-backed implementation.
    """

    def __init__(self) -> None:
        self._flow_store: dict[str, dict[str, object]] = {}

    def _build_msal_app(self, config: EntraConfig) -> msal.ConfidentialClientApplication:
        return msal.ConfidentialClientApplication(
            client_id=config.client_id,
            client_credential=config.client_secret,
            authority=f"https://login.microsoftonline.com/{config.tenant_id}",
        )

    async def get_authorization_url(self, state: str, config: EntraConfig) -> str:
        app = self._build_msal_app(config)
        flow: dict[str, object] = await asyncio.to_thread(
            lambda: app.initiate_auth_code_flow(
                scopes=_SCOPES,
                redirect_uri=config.redirect_uri,
                state=state,
            )
        )
        self._flow_store[state] = flow
        return str(flow["auth_uri"])

    async def exchange_code(self, code: str, state: str, config: EntraConfig) -> OAuthUserInfo:
        flow = self._flow_store.pop(state, None)
        if flow is None:
            raise OAuthProviderError("OAuth flow not found. The session may have expired.")
        app = self._build_msal_app(config)
        result: dict[str, object] = await asyncio.to_thread(
            lambda: app.acquire_token_by_auth_code_flow(
                auth_code_flow=flow,
                auth_response={"code": code, "state": state},
            )
        )

        if "error" in result:
            logger.error(
                "Entra token exchange failed",
                extra={
                    "event": "entra_token_error",
                    "error": result.get("error"),
                    "error_description": result.get("error_description"),
                },
            )
            raise OAuthProviderError(f"Entra token exchange failed: {result.get('error_description')}")

        claims: dict[str, object] = result.get("id_token_claims", {})  # type: ignore[assignment]
        email = _resolve_email(claims)
        full_name = _resolve_full_name(claims, email)

        oid = claims.get("oid")
        if not isinstance(oid, str):
            raise OAuthProviderError("Missing or invalid 'oid' claim in Entra token")

        return OAuthUserInfo(
            provider_id=oid,
            email=email,
            full_name=full_name,
            provider="entra",
        )
