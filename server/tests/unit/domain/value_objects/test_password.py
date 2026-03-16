import pytest

from raggae.domain.exceptions.validation_errors import WeakPasswordError
from raggae.domain.value_objects.password import Password


class TestPassword:
    def test_create_password_with_valid_format(self) -> None:
        # When
        password = Password("SecurePass123!")

        # Then
        assert password.value == "SecurePass123!"

    @pytest.mark.parametrize(
        "weak_password,reason",
        [
            ("short1!", "too short"),
            ("alllowercase1!", "no uppercase"),
            ("ALLUPPERCASE1!", "no lowercase"),
            ("NoDigitsHere!", "no digit"),
            ("", "empty"),
        ],
    )
    def test_create_password_with_weak_format_raises_error(
        self, weak_password: str, reason: str
    ) -> None:
        # When / Then
        with pytest.raises(WeakPasswordError):
            Password(weak_password)
