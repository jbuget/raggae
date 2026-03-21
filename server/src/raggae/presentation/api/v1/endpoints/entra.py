import logging
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from itsdangerous import BadData, URLSafeSerializer

from raggae.application.dto.oauth_state import OAuthState
from raggae.infrastructure.config.settings import settings
from raggae.presentation.api.dependencies import (
    get_handle_oauth_callback_use_case,
    get_initiate_oauth_login_use_case,
    get_oauth_code_store,
)
from raggae.presentation.api.v1.schemas.auth_schemas import OAuthLoginResponse, OAuthTokenRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/entra", tags=["auth"])

_COOKIE_NAME = "oauth_state"
_COOKIE_MAX_AGE = 300  # 5 minutes


def _state_signer() -> URLSafeSerializer:
    return URLSafeSerializer(settings.secret_key, salt="oauth_state")


def _serialize_state(state: OAuthState) -> str:
    return _state_signer().dumps(
        {
            "csrf_token": state.csrf_token,
            "redirect_url": state.redirect_url,
            "expires_at": state.expires_at.isoformat(),
        }
    )


def _deserialize_state(signed: str) -> OAuthState | None:
    try:
        data = _state_signer().loads(signed)
        return OAuthState(
            csrf_token=data["csrf_token"],
            redirect_url=data["redirect_url"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )
    except (BadData, KeyError, ValueError):
        return None


def _not_implemented() -> Response:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Microsoft Entra SSO is not enabled on this instance.",
    )


@router.get("/login")
async def entra_login(
    request: Request,
    redirect_url: str = "/",
) -> Response:
    """Initiate Microsoft Entra SSO flow. Redirects to the Microsoft login page."""
    if not settings.entra_enabled:
        return _not_implemented()

    use_case = get_initiate_oauth_login_use_case()
    result = await use_case.execute(redirect_url=redirect_url)

    signed_state = _serialize_state(result.state)
    response = RedirectResponse(url=result.authorization_url, status_code=302)
    response.set_cookie(
        key=_COOKIE_NAME,
        value=signed_state,
        httponly=True,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
    )
    return response


@router.get("/callback")
async def entra_callback(
    code: str,
    state: str,
    oauth_state: str | None = Cookie(default=None, alias=_COOKIE_NAME),
) -> Response:
    """Handle Microsoft Entra callback. Exchanges code and redirects to frontend."""
    if not settings.entra_enabled:
        return _not_implemented()

    if oauth_state is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing state cookie.")

    parsed_state = _deserialize_state(oauth_state)
    if parsed_state is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state cookie.")

    if parsed_state.csrf_token != state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State mismatch.")

    if parsed_state.is_expired():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State expired.")

    use_case = get_handle_oauth_callback_use_case()
    from raggae.presentation.api.dependencies import get_entra_config

    config = get_entra_config()

    try:
        from raggae.domain.exceptions.user_exceptions import (
            OAuthDomainNotAllowedError,
            UserAlreadyInactiveError,
        )

        login_result = await use_case.execute(code=code, state=parsed_state, config=config)
    except OAuthDomainNotAllowedError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your email domain is not authorized.",
        ) from exc
    except UserAlreadyInactiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is disabled.",
        ) from exc

    one_time_code = str(uuid4())
    code_store = get_oauth_code_store()
    await code_store.store(one_time_code, login_result, ttl_seconds=30)

    redirect_url = parsed_state.redirect_url or "/"
    frontend_callback = f"{settings.frontend_url}/auth/callback?code={one_time_code}&redirect={redirect_url}"

    response = RedirectResponse(url=frontend_callback, status_code=302)
    response.delete_cookie(key=_COOKIE_NAME)
    return response


@router.post("/token", response_model=OAuthLoginResponse)
async def entra_token(body: OAuthTokenRequest) -> OAuthLoginResponse:
    """Exchange a one-time code for a JWT access token."""
    if not settings.entra_enabled:
        _not_implemented()

    code_store = get_oauth_code_store()
    login_result = await code_store.consume(body.code)

    if login_result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired code.",
        )

    return OAuthLoginResponse(
        access_token=login_result.access_token,
        token_type=login_result.token_type,
        is_new_user=login_result.is_new_user,
        account_linked=login_result.account_linked,
    )
