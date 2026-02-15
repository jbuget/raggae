from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class User:
    """User domain entity. Immutable."""

    id: UUID
    email: str
    hashed_password: str
    full_name: str
    is_active: bool
    created_at: datetime
