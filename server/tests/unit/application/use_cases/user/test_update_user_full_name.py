from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.use_cases.user.update_user_full_name import UpdateUserFullName
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import UserNotFoundError


class TestUpdateUserFullName:
    @pytest.fixture
    def mock_user_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(self, mock_user_repository: AsyncMock) -> UpdateUserFullName:
        return UpdateUserFullName(user_repository=mock_user_repository)

    async def test_update_user_full_name_success(
        self,
        use_case: UpdateUserFullName,
        mock_user_repository: AsyncMock,
    ) -> None:
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed",
            full_name="Old Name",
            is_active=True,
            created_at=datetime.now(UTC),
        )
        mock_user_repository.find_by_id.return_value = user

        result = await use_case.execute(user_id=user.id, full_name="New Name")

        assert result.full_name == "New Name"
        mock_user_repository.save.assert_called_once()

    async def test_update_user_full_name_user_not_found_raises_error(
        self,
        use_case: UpdateUserFullName,
        mock_user_repository: AsyncMock,
    ) -> None:
        mock_user_repository.find_by_id.return_value = None

        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id=uuid4(), full_name="New Name")
