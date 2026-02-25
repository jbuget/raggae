from uuid import UUID

from raggae.application.dto.user_dto import UserDTO
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.exceptions.user_exceptions import UserNotFoundError


class GetCurrentUser:
    """Use Case: Get current authenticated user profile."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def execute(self, user_id: UUID) -> UserDTO:
        user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found")
        return UserDTO.from_entity(user)
