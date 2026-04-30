from uuid import UUID

from raggae.domain.entities.user_project_defaults import UserProjectDefaults


class InMemoryUserProjectDefaultsRepository:
    """In-memory user project defaults repository for testing."""

    def __init__(self) -> None:
        self._store: dict[UUID, UserProjectDefaults] = {}

    async def find_by_user_id(self, user_id: UUID) -> UserProjectDefaults | None:
        return self._store.get(user_id)

    async def save(self, defaults: UserProjectDefaults) -> None:
        self._store[defaults.user_id] = defaults
