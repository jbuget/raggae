from uuid import UUID

from raggae.application.dto.user_project_defaults_dto import UserProjectDefaultsDTO
from raggae.application.interfaces.repositories.user_project_defaults_repository import (
    UserProjectDefaultsRepository,
)
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.exceptions.user_exceptions import UserNotFoundError


class GetUserProjectDefaults:
    """Use Case: Get the project defaults configured at user level."""

    def __init__(
        self,
        user_repository: UserRepository,
        user_project_defaults_repository: UserProjectDefaultsRepository,
    ) -> None:
        self._user_repository = user_repository
        self._user_project_defaults_repository = user_project_defaults_repository

    async def execute(self, user_id: UUID) -> UserProjectDefaultsDTO | None:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        defaults = await self._user_project_defaults_repository.find_by_user_id(user_id)
        if defaults is None:
            return None
        return UserProjectDefaultsDTO.from_entity(defaults)
