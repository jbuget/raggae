from uuid import UUID

from raggae.domain.entities.user import User


class InMemoryUserRepository:
    """In-memory user repository for testing."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def save(self, user: User) -> None:
        self._users[user.id] = user

    async def find_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def find_by_email(self, email: str) -> User | None:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def find_by_entra_id(self, entra_id: str) -> User | None:
        for user in self._users.values():
            if user.entra_id == entra_id:
                return user
        return None
