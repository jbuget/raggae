import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import uuid4

from raggae.application.config.entra_config import EntraConfig
from raggae.application.dto.oauth_state import OAuthState
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.application.interfaces.services.oauth_provider import OAuthProvider, OAuthUserInfo
from raggae.application.interfaces.services.token_service import TokenService
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import (
    OAuthDomainNotAllowedError,
    UserAlreadyInactiveError,
)
from raggae.domain.value_objects.locale import Locale

logger = logging.getLogger(__name__)


@dataclass
class OAuthLoginResult:
    """Result of a successful OAuth authentication."""

    access_token: str
    token_type: str = "bearer"
    is_new_user: bool = False
    account_linked: bool = False


class HandleOAuthCallback:
    """Use Case: Process an OAuth provider callback.

    Handles account lookup by entra_id, account linking by email,
    new account creation, email drift correction and domain validation.
    """

    def __init__(
        self,
        oauth_provider: OAuthProvider,
        user_repository: UserRepository,
        token_service: TokenService,
    ) -> None:
        self._oauth_provider = oauth_provider
        self._user_repository = user_repository
        self._token_service = token_service

    async def execute(self, code: str, state: OAuthState, config: EntraConfig) -> OAuthLoginResult:
        user_info = await self._oauth_provider.exchange_code(
            code=code, state=state.csrf_token, config=config
        )

        if not config.is_domain_allowed(user_info.email):
            logger.warning(
                "OAuth login rejected — domain not allowed",
                extra={
                    "event": "domain_rejected",
                    "provider": user_info.provider,
                    "email": user_info.email,
                },
            )
            raise OAuthDomainNotAllowedError(f"Email domain not allowed: {user_info.email}")

        user = await self._user_repository.find_by_entra_id(user_info.provider_id)
        if user is not None:
            return await self._login_existing_entra_user(user, user_info)

        user = await self._user_repository.find_by_email(user_info.email)
        if user is not None:
            return await self._link_local_user(user, user_info)

        return await self._create_new_sso_user(user_info)

    async def _login_existing_entra_user(
        self, user: User, user_info: OAuthUserInfo
    ) -> OAuthLoginResult:
        if not user.is_active:
            raise UserAlreadyInactiveError()

        if user.email != user_info.email:
            user = user.update_email(user_info.email)
            await self._user_repository.save(user)
            logger.info(
                "Entra email updated",
                extra={
                    "event": "email_updated",
                    "provider": user_info.provider,
                    "user_id": str(user.id),
                    "new_email": user_info.email,
                },
            )

        logger.info(
            "SSO login successful",
            extra={
                "event": "sso_login",
                "provider": user_info.provider,
                "user_id": str(user.id),
            },
        )
        token = self._token_service.create_access_token(user.id)
        return OAuthLoginResult(access_token=token)

    async def _link_local_user(self, user: User, user_info: OAuthUserInfo) -> OAuthLoginResult:
        if not user.is_active:
            raise UserAlreadyInactiveError()

        user = user.link_entra(user_info.provider_id)
        await self._user_repository.save(user)

        logger.info(
            "Local account linked to Entra",
            extra={
                "event": "account_linked",
                "provider": user_info.provider,
                "user_id": str(user.id),
                "email": user_info.email,
            },
        )
        token = self._token_service.create_access_token(user.id)
        return OAuthLoginResult(access_token=token, account_linked=True)

    async def _create_new_sso_user(self, user_info: OAuthUserInfo) -> OAuthLoginResult:
        user = User(
            id=uuid4(),
            email=user_info.email,
            hashed_password=None,
            full_name=user_info.full_name,
            is_active=True,
            created_at=datetime.now(UTC),
            locale=Locale.EN,
            entra_id=user_info.provider_id,
        )
        await self._user_repository.save(user)

        logger.info(
            "New SSO account created",
            extra={
                "event": "account_created",
                "provider": user_info.provider,
                "user_id": str(user.id),
                "email": user_info.email,
            },
        )
        token = self._token_service.create_access_token(user.id)
        return OAuthLoginResult(access_token=token, is_new_user=True)
