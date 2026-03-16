import pytest

from raggae.domain.exceptions.validation_errors import InvalidEmailError
from raggae.domain.value_objects.email import Email


class TestEmail:
    def test_create_email_with_valid_format(self) -> None:
        # When
        email = Email("valid@example.com")

        # Then
        assert email.value == "valid@example.com"

    @pytest.mark.parametrize(
        "invalid_email",
        [
            "not-an-email",
            "@example.com",
            "user@",
            "user @example.com",
            "",
        ],
    )
    def test_create_email_with_invalid_format_raises_error(self, invalid_email: str) -> None:
        # When / Then
        with pytest.raises(InvalidEmailError):
            Email(invalid_email)
