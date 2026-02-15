from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.use_cases.user.register_user import RegisterUser
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import UserAlreadyExistsError


class TestRegisterUser:
    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_password_hasher(self) -> Mock:
        hasher = Mock()
        hasher.hash.return_value = "hashed_password"
        return hasher

    @pytest.fixture
    def use_case(self, mock_user_repository: AsyncMock, mock_password_hasher: Mock) -> RegisterUser:
        return RegisterUser(
            user_repository=mock_user_repository,
            password_hasher=mock_password_hasher,
        )

    async def test_register_user_success(
        self,
        use_case: RegisterUser,
        mock_user_repository: AsyncMock,
        mock_password_hasher: Mock,
    ) -> None:
        # Given
        mock_user_repository.find_by_email.return_value = None

        # When
        result = await use_case.execute(
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User",
        )

        # Then
        assert result.email == "test@example.com"
        assert result.full_name == "Test User"
        assert result.is_active is True
        mock_password_hasher.hash.assert_called_once_with("SecurePass123!")
        mock_user_repository.save.assert_called_once()

    async def test_register_user_email_already_exists(
        self,
        use_case: RegisterUser,
        mock_user_repository: AsyncMock,
    ) -> None:
        # Given
        existing_user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="Existing",
            is_active=True,
            created_at=datetime.now(UTC),
        )
        mock_user_repository.find_by_email.return_value = existing_user

        # When / Then
        with pytest.raises(UserAlreadyExistsError):
            await use_case.execute(
                email="test@example.com",
                password="SecurePass123!",
                full_name="Test User",
            )
