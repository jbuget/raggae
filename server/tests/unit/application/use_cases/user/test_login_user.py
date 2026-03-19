from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.use_cases.user.login_user import LoginUser
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import InvalidCredentialsError


class TestLoginUser:
    @pytest.fixture
    def user_id(self) -> None:
        return uuid4()

    @pytest.fixture
    def existing_user(self, user_id: None) -> User:
        return User(
            id=user_id,
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(UTC),
        )

    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_password_hasher(self) -> Mock:
        hasher = Mock()
        hasher.verify.return_value = True
        return hasher

    @pytest.fixture
    def mock_token_service(self) -> Mock:
        token_service = Mock()
        token_service.create_access_token.return_value = "jwt-token"
        return token_service

    @pytest.fixture
    def use_case(
        self,
        mock_user_repository: AsyncMock,
        mock_password_hasher: Mock,
        mock_token_service: Mock,
    ) -> LoginUser:
        return LoginUser(
            user_repository=mock_user_repository,
            password_hasher=mock_password_hasher,
            token_service=mock_token_service,
        )

    async def test_login_user_success(
        self,
        use_case: LoginUser,
        mock_user_repository: AsyncMock,
        existing_user: User,
    ) -> None:
        # Given
        mock_user_repository.find_by_email.return_value = existing_user

        # When
        result = await use_case.execute(
            email="test@example.com",
            password="SecurePass123!",
        )

        # Then
        assert result.access_token == "jwt-token"
        assert result.token_type == "bearer"

    async def test_login_user_unknown_email_raises_error(
        self,
        use_case: LoginUser,
        mock_user_repository: AsyncMock,
    ) -> None:
        # Given
        mock_user_repository.find_by_email.return_value = None

        # When / Then
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(email="unknown@example.com", password="Pass123!")

    async def test_login_user_wrong_password_raises_error(
        self,
        use_case: LoginUser,
        mock_user_repository: AsyncMock,
        mock_password_hasher: Mock,
        existing_user: User,
    ) -> None:
        # Given
        mock_user_repository.find_by_email.return_value = existing_user
        mock_password_hasher.verify.return_value = False

        # When / Then
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(email="test@example.com", password="WrongPass123!")

    async def test_login_user_sso_only_account_raises_invalid_credentials(
        self,
        use_case: LoginUser,
        mock_user_repository: AsyncMock,
    ) -> None:
        # Given — compte SSO-only, pas de mot de passe local
        sso_user = User(
            id=uuid4(),
            email="sso@example.com",
            hashed_password=None,
            full_name="SSO User",
            is_active=True,
            created_at=datetime.now(UTC),
            entra_id="oid-abc-123",
        )
        mock_user_repository.find_by_email.return_value = sso_user

        # When / Then — même erreur générique, aucun info leak sur le type de compte
        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(email="sso@example.com", password="AnyPass123!")
