from uuid import UUID

from raggae.application.dto.project_defaults_dto import ProjectDefaultsDTO
from raggae.application.interfaces.repositories.project_defaults_repository import (
    ProjectDefaultsRepository,
)
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.exceptions.user_exceptions import UserNotFoundError
from raggae.domain.value_objects.project_defaults_owner_type import ProjectDefaultsOwnerType


class GetUserProjectDefaults:
    """Use Case: Get the project defaults configured at user level."""

    def __init__(
        self,
        user_repository: UserRepository,
        project_defaults_repository: ProjectDefaultsRepository,
    ) -> None:
        self._user_repository = user_repository
        self._project_defaults_repository = project_defaults_repository

    async def execute(self, user_id: UUID) -> ProjectDefaultsDTO | None:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        defaults = await self._project_defaults_repository.find_by_owner(
            user_id, ProjectDefaultsOwnerType.USER
        )
        if defaults is None:
            return None
        return ProjectDefaultsDTO.from_entity(defaults)
