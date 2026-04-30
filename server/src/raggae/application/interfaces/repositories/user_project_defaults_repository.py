from typing import Protocol
from uuid import UUID

from raggae.domain.entities.user_project_defaults import UserProjectDefaults


class UserProjectDefaultsRepository(Protocol):
    """Interface for user project defaults persistence."""

    async def find_by_user_id(self, user_id: UUID) -> UserProjectDefaults | None: ...

    async def save(self, defaults: UserProjectDefaults) -> None: ...
