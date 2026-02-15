from dataclasses import dataclass

from raggae.domain.exceptions.validation_errors import WeakPasswordError

_MIN_LENGTH = 8


@dataclass(frozen=True)
class Password:
    """Value Object for validated plain-text passwords (pre-hashing)."""

    value: str

    def __post_init__(self) -> None:
        if len(self.value) < _MIN_LENGTH:
            raise WeakPasswordError("Password must be at least 8 characters")
        if not any(c.isupper() for c in self.value):
            raise WeakPasswordError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in self.value):
            raise WeakPasswordError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in self.value):
            raise WeakPasswordError("Password must contain at least one digit")
