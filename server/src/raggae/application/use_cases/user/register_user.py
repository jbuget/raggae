from datetime import UTC, datetime
from uuid import uuid4

from raggae.application.dto.user_dto import UserDTO
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.application.interfaces.services.password_hasher import PasswordHasher
from raggae.domain.entities.user import User
from raggae.domain.exceptions.user_exceptions import UserAlreadyExistsError


class RegisterUser:
    """Use Case: Register a new user."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher

    async def execute(self, email: str, password: str, full_name: str) -> UserDTO:
        existing = await self._user_repository.find_by_email(email)
        if existing:
            raise UserAlreadyExistsError(f"User with email {email} already exists")

        user = User(
            id=uuid4(),
            email=email,
            hashed_password=self._password_hasher.hash(password),
            full_name=full_name,
            is_active=True,
            created_at=datetime.now(UTC),
        )

        await self._user_repository.save(user)

        return UserDTO.from_entity(user)
