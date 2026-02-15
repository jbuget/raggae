from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.user import User


@dataclass
class UserDTO:
    """Data Transfer Object for User, excluding sensitive fields."""

    id: UUID
    email: str
    full_name: str
    is_active: bool
    created_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> "UserDTO":
        return cls(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
        )
