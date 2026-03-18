from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import UUID

from raggae.domain.exceptions.user_exceptions import UserAlreadyInactiveError
from raggae.domain.value_objects.locale import Locale


@dataclass(frozen=True)
class User:
    """User domain entity. Immutable."""

    id: UUID
    email: str
    hashed_password: str
    full_name: str
    is_active: bool
    created_at: datetime
    locale: Locale = field(default=Locale.EN)

    def deactivate(self) -> "User":
        """Deactivate the user. Raises if already inactive."""
        if not self.is_active:
            raise UserAlreadyInactiveError()
        return replace(self, is_active=False)
