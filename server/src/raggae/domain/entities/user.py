from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.exceptions.user_exceptions import UserAlreadyInactiveError


@dataclass(frozen=True)
class User:
    """User domain entity. Immutable."""

    id: UUID
    email: str
    hashed_password: str
    full_name: str
    is_active: bool
    created_at: datetime

    def deactivate(self) -> "User":
        """Deactivate the user. Raises if already inactive."""
        if not self.is_active:
            raise UserAlreadyInactiveError()
        return replace(self, is_active=False)
