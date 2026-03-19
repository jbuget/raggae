from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.config.entra_config import EntraConfig
from raggae.application.dto.oauth_state import OAuthState
from raggae.application.interfaces.services.oauth_provider import OAuthUserInfo
from raggae.application.use_cases.user.handle_oauth_callback import HandleOAuthCallback
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import (
    OAuthDomainNotAllowedError,
    UserAlreadyInactiveError,
)
from raggae.infrastructure.database.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


def make_state(redirect_url: str = "/") -> OAuthState:
    return OAuthState(
        csrf_token="csrf-token-abc",
        redirect_url=redirect_url,
        expires_at=datetime.now(UTC) + timedelta(minutes=5),
    )


def make_user_info(
    email: str = "j.buget@waat.fr",
    provider_id: str = "oid-abc-123",
    full_name: str = "Jérémy Buget",
) -> OAuthUserInfo:
    return OAuthUserInfo(
        provider_id=provider_id,
        email=email,
        full_name=full_name,
        provider="entra",
    )


def make_local_user(
    email: str = "j.buget@waat.fr",
    is_active: bool = True,
) -> User:
    return User(
        id=uuid4(),
        email=email,
        hashed_password="hashed_pwd",
        full_name="Jérémy Buget",
        is_active=is_active,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def entra_config() -> EntraConfig:
    return EntraConfig(
        client_id="client-id",
        client_secret="client-secret",
        tenant_id="tenant-id",
        redirect_uri="https://app.example.com/callback",
        allowed_domains=["waat.fr"],
    )


@pytest.fixture
def entra_config_no_domain_restriction() -> EntraConfig:
    return EntraConfig(
        client_id="client-id",
        client_secret="client-secret",
        tenant_id="tenant-id",
        redirect_uri="https://app.example.com/callback",
        allowed_domains=[],
    )


@pytest.fixture
def mock_oauth_provider() -> AsyncMock:
    provider = AsyncMock()
    provider.exchange_code.return_value = make_user_info()
    return provider


@pytest.fixture
def mock_token_service() -> Mock:
    svc = Mock()
    svc.create_access_token.return_value = "jwt-token"
    return svc


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def use_case(
    mock_oauth_provider: AsyncMock,
    user_repository: InMemoryUserRepository,
    mock_token_service: Mock,
) -> HandleOAuthCallback:
    return HandleOAuthCallback(
        oauth_provider=mock_oauth_provider,
        user_repository=user_repository,
        token_service=mock_token_service,
    )


class TestHandleOAuthCallback:
    async def test_new_user_is_created_and_jwt_returned(
        self,
        use_case: HandleOAuthCallback,
        entra_config: EntraConfig,
    ) -> None:
        # When
        result = await use_case.execute(
            code="auth-code",
            state=make_state(),
            config=entra_config,
        )

        # Then
        assert result.access_token == "jwt-token"
        assert result.token_type == "bearer"
        assert result.is_new_user is True
        assert result.account_linked is False

    async def test_new_user_account_has_entra_id_and_no_password(
        self,
        use_case: HandleOAuthCallback,
        user_repository: InMemoryUserRepository,
        entra_config: EntraConfig,
    ) -> None:
        # When
        await use_case.execute(code="auth-code", state=make_state(), config=entra_config)

        # Then
        saved = await user_repository.find_by_entra_id("oid-abc-123")
        assert saved is not None
        assert saved.entra_id == "oid-abc-123"
        assert saved.hashed_password is None
        assert saved.email == "j.buget@waat.fr"
        assert saved.full_name == "Jérémy Buget"
        assert saved.is_active is True

    async def test_existing_user_by_entra_id_is_logged_in_directly(
        self,
        use_case: HandleOAuthCallback,
        user_repository: InMemoryUserRepository,
        entra_config: EntraConfig,
    ) -> None:
        # Given — user already linked to Entra
        existing = User(
            id=uuid4(),
            email="j.buget@waat.fr",
            hashed_password=None,
            full_name="Jérémy Buget",
            is_active=True,
            created_at=datetime.now(UTC),
            entra_id="oid-abc-123",
        )
        await user_repository.save(existing)

        # When
        result = await use_case.execute(
            code="auth-code", state=make_state(), config=entra_config
        )

        # Then
        assert result.access_token == "jwt-token"
        assert result.is_new_user is False
        assert result.account_linked is False

    async def test_existing_local_user_is_linked_to_entra(
        self,
        use_case: HandleOAuthCallback,
        user_repository: InMemoryUserRepository,
        entra_config: EntraConfig,
    ) -> None:
        # Given — user with email/password, no entra_id yet
        local_user = make_local_user()
        await user_repository.save(local_user)

        # When
        result = await use_case.execute(
            code="auth-code", state=make_state(), config=entra_config
        )

        # Then
        assert result.account_linked is True
        assert result.is_new_user is False
        linked = await user_repository.find_by_entra_id("oid-abc-123")
        assert linked is not None
        assert linked.id == local_user.id
        assert linked.hashed_password == "hashed_pwd"  # mot de passe conservé

    async def test_email_drift_is_corrected_when_found_by_entra_id(
        self,
        use_case: HandleOAuthCallback,
        user_repository: InMemoryUserRepository,
        mock_oauth_provider: AsyncMock,
        entra_config: EntraConfig,
    ) -> None:
        # Given — Entra now returns a new email for same oid
        mock_oauth_provider.exchange_code.return_value = make_user_info(
            email="jeremy.buget@waat.fr"
        )
        existing = User(
            id=uuid4(),
            email="j.buget@waat.fr",
            hashed_password=None,
            full_name="Jérémy Buget",
            is_active=True,
            created_at=datetime.now(UTC),
            entra_id="oid-abc-123",
        )
        await user_repository.save(existing)

        # When
        await use_case.execute(code="auth-code", state=make_state(), config=entra_config)

        # Then — email updated silently
        updated = await user_repository.find_by_entra_id("oid-abc-123")
        assert updated is not None
        assert updated.email == "jeremy.buget@waat.fr"

    async def test_domain_not_allowed_raises_error(
        self,
        use_case: HandleOAuthCallback,
        mock_oauth_provider: AsyncMock,
        entra_config: EntraConfig,
    ) -> None:
        # Given — user from a non-allowed domain
        mock_oauth_provider.exchange_code.return_value = make_user_info(
            email="j.buget@pix.fr"
        )

        # When / Then
        with pytest.raises(OAuthDomainNotAllowedError):
            await use_case.execute(code="auth-code", state=make_state(), config=entra_config)

    async def test_no_domain_restriction_allows_any_email(
        self,
        mock_oauth_provider: AsyncMock,
        user_repository: InMemoryUserRepository,
        mock_token_service: Mock,
        entra_config_no_domain_restriction: EntraConfig,
    ) -> None:
        # Given — config with no domain restriction
        mock_oauth_provider.exchange_code.return_value = make_user_info(email="user@any.com")
        use_case = HandleOAuthCallback(
            oauth_provider=mock_oauth_provider,
            user_repository=user_repository,
            token_service=mock_token_service,
        )

        # When / Then — no exception raised
        result = await use_case.execute(
            code="auth-code",
            state=make_state(),
            config=entra_config_no_domain_restriction,
        )
        assert result.is_new_user is True

    async def test_inactive_user_found_by_email_raises_error(
        self,
        use_case: HandleOAuthCallback,
        user_repository: InMemoryUserRepository,
        entra_config: EntraConfig,
    ) -> None:
        # Given — inactive local account with same email
        inactive = make_local_user(is_active=False)
        await user_repository.save(inactive)

        # When / Then
        with pytest.raises(UserAlreadyInactiveError):
            await use_case.execute(code="auth-code", state=make_state(), config=entra_config)

    async def test_inactive_user_found_by_entra_id_raises_error(
        self,
        use_case: HandleOAuthCallback,
        user_repository: InMemoryUserRepository,
        entra_config: EntraConfig,
    ) -> None:
        # Given — inactive SSO account already linked
        inactive = User(
            id=uuid4(),
            email="j.buget@waat.fr",
            hashed_password=None,
            full_name="Jérémy Buget",
            is_active=False,
            created_at=datetime.now(UTC),
            entra_id="oid-abc-123",
        )
        await user_repository.save(inactive)

        # When / Then
        with pytest.raises(UserAlreadyInactiveError):
            await use_case.execute(code="auth-code", state=make_state(), config=entra_config)
