from dataclasses import dataclass

from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.application.interfaces.services.password_hasher import PasswordHasher
from raggae.application.interfaces.services.token_service import TokenService
from raggae.domain.exceptions.user_exceptions import InvalidCredentialsError


@dataclass
class LoginResult:
    """Result of a successful login."""

    access_token: str
    token_type: str = "bearer"


class LoginUser:
    """Use Case: Authenticate a user and return a JWT token."""

    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._token_service = token_service

    async def execute(self, email: str, password: str) -> LoginResult:
        user = await self._user_repository.find_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not self._password_hasher.verify(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        access_token = self._token_service.create_access_token(user.id)

        return LoginResult(access_token=access_token)
