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
    hashed_password: str | None
    full_name: str
    is_active: bool
    created_at: datetime
    locale: Locale = field(default=Locale.EN)
    entra_id: str | None = field(default=None)

    def deactivate(self) -> "User":
        """Deactivate the user. Raises if already inactive."""
        if not self.is_active:
            raise UserAlreadyInactiveError()
        return replace(self, is_active=False)

    def has_local_credentials(self) -> bool:
        """Return True if the user can authenticate with email/password."""
        return self.hashed_password is not None

    def link_entra(self, entra_id: str) -> "User":
        """Return a new User with the given Microsoft Entra oid associated."""
        return replace(self, entra_id=entra_id)

    def update_email(self, email: str) -> "User":
        """Return a new User with an updated email address."""
        return replace(self, email=email)
