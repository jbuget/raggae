from dataclasses import replace
from uuid import UUID

from raggae.application.dto.user_dto import UserDTO
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.exceptions.user_exceptions import UserNotFoundError
from raggae.domain.value_objects.locale import Locale


class UpdateUserLocale:
    """Use Case: Update current user's locale preference."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, user_id: UUID, locale: Locale) -> UserDTO:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        updated_user = replace(user, locale=locale)
        await self._user_repository.save(updated_user)
        return UserDTO.from_entity(updated_user)
