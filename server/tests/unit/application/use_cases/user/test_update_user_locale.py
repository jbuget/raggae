from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.user.update_user_locale import UpdateUserLocale
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import UserNotFoundError
from raggae.domain.value_objects.locale import Locale


class TestUpdateUserLocale:
    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_user_repository: AsyncMock) -> UpdateUserLocale:
        return UpdateUserLocale(user_repository=mock_user_repository)

    async def test_update_user_locale_success_changes_locale(
        self,
        use_case: UpdateUserLocale,
        mock_user_repository: AsyncMock,
    ) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
            locale=Locale.EN,
        )
        mock_user_repository.find_by_id.return_value = user

        # When
        result = await use_case.execute(user_id=user.id, locale=Locale.FR)

        # Then
        assert result.locale == Locale.FR
        mock_user_repository.save.assert_called_once()

    async def test_update_user_locale_user_not_found_raises_error(
        self,
        use_case: UpdateUserLocale,
        mock_user_repository: AsyncMock,
    ) -> None:
        # Given
        mock_user_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id=uuid4(), locale=Locale.FR)

    async def test_update_user_locale_persists_to_repository(
        self,
        use_case: UpdateUserLocale,
        mock_user_repository: AsyncMock,
    ) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
            locale=Locale.EN,
        )
        mock_user_repository.find_by_id.return_value = user

        # When
        await use_case.execute(user_id=user.id, locale=Locale.FR)

        # Then
        saved_user = mock_user_repository.save.call_args[0][0]
        assert saved_user.locale == Locale.FR
