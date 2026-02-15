import re
from dataclasses import dataclass

from raggae.domain.exceptions.validation_errors import InvalidEmailError

_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


@dataclass(frozen=True)
class Email:
    """Value Object for validated email addresses."""

    value: str

    def __post_init__(self) -> None:
        if not _EMAIL_PATTERN.match(self.value):
            raise InvalidEmailError(f"Invalid email format: {self.value}")
