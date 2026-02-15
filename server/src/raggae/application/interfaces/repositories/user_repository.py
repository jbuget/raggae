from typing import Protocol
from uuid import UUID

from raggae.domain.entities.user import User


class UserRepository(Protocol):
    """Interface for user persistence."""

    async def save(self, user: User) -> None: ...

    async def find_by_id(self, user_id: UUID) -> User | None: ...

    async def find_by_email(self, email: str) -> User | None: ...
