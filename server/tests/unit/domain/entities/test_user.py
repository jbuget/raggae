from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.dto.user_dto import UserDTO
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import UserAlreadyInactiveError
from raggae.domain.value_objects.locale import Locale


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

    def test_create_user_has_default_locale_en(self) -> None:
        # Given / When
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # Then
        assert user.locale == Locale.EN

    def test_create_user_with_explicit_locale_fr(self) -> None:
        # Given / When
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
            locale=Locale.FR,
        )

        # Then
        assert user.locale == Locale.FR

    def test_user_dto_from_entity_maps_locale(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
            locale=Locale.FR,
        )

        # When
        dto = UserDTO.from_entity(user)

        # Then
        assert dto.locale == Locale.FR

    def test_user_locale_is_immutable(self) -> None:
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
            user.locale = Locale.FR  # type: ignore[misc]

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

    def test_create_user_without_hashed_password_is_sso_only(self) -> None:
        # Given / When
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password=None,
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # Then
        assert user.hashed_password is None

    def test_has_local_credentials_returns_true_when_hashed_password_set(self) -> None:
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
        assert user.has_local_credentials() is True

    def test_has_local_credentials_returns_false_when_hashed_password_is_none(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password=None,
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # When / Then
        assert user.has_local_credentials() is False

    def test_create_user_has_no_entra_id_by_default(self) -> None:
        # Given / When
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password="hashed_pwd",
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # Then
        assert user.entra_id is None

    def test_link_entra_returns_new_user_with_entra_id(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password=None,
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )
        entra_id = "oid-abc-123"

        # When
        linked = user.link_entra(entra_id)

        # Then
        assert linked.entra_id == entra_id
        assert linked.id == user.id
        assert linked.email == user.email

    def test_link_entra_does_not_mutate_original_user(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="test@example.com",
            hashed_password=None,
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # When
        user.link_entra("oid-abc-123")

        # Then
        assert user.entra_id is None

    def test_update_email_returns_new_user_with_updated_email(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="old@example.com",
            hashed_password=None,
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
            entra_id="oid-abc-123",
        )

        # When
        updated = user.update_email("new@example.com")

        # Then
        assert updated.email == "new@example.com"
        assert updated.id == user.id
        assert updated.entra_id == user.entra_id

    def test_update_email_does_not_mutate_original_user(self) -> None:
        # Given
        user = User(
            id=uuid4(),
            email="old@example.com",
            hashed_password=None,
            full_name="John Doe",
            is_active=True,
            created_at=datetime.now(UTC),
        )

        # When
        user.update_email("new@example.com")

        # Then
        assert user.email == "old@example.com"
