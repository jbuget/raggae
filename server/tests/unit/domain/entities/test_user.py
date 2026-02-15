from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import UserAlreadyInactiveError


class TestUser:
    def test_create_user_with_valid_data(self) -> None:
        # Given
        user_id = uuid4()
        email = "test@example.com"
        now = datetime.now(UTC)

        # When
        user = User(
            id=user_id,
            email=email,
            hashed_password="hashed_pwd",
            full_name="John Doe",
            is_active=True,
            created_at=now,
        )

        # Then
        assert user.id == user_id
        assert user.email == email
        assert user.hashed_password == "hashed_pwd"
        assert user.full_name == "John Doe"
        assert user.is_active is True
        assert user.created_at == now

    def test_user_is_immutable(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # When / Then
        with pytest.raises(FrozenInstanceError):
            user.email = "other@example.com"  # type: ignore[misc]

    def test_deactivate_active_user(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # When
        deactivated = user.deactivate()

        # Then
        assert deactivated.is_active is False
        assert deactivated.id == user.id
        assert deactivated.email == user.email

    def test_deactivate_inactive_user_raises_error(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="John Doe",
            is_active=False,
            created_at=datetime.now(UTC),
        )

        # When / Then
        with pytest.raises(UserAlreadyInactiveError):
            user.deactivate()
