from typing import Protocol


class PasswordHasher(Protocol):
    """Interface for password hashing."""

    def hash(self, password: str) -> str: ...

    def verify(self, password: str, hashed: str) -> bool: ...
