from raggae.application.use_cases.user.login_user import LoginUser
from raggae.application.use_cases.user.register_user import RegisterUser
from raggae.infrastructure.database.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from raggae.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from raggae.infrastructure.services.jwt_token_service import JwtTokenService

_user_repository = InMemoryUserRepository()
_password_hasher = BcryptPasswordHasher()
_token_service = JwtTokenService(secret_key="dev-secret-key", algorithm="HS256")


def get_register_user_use_case() -> RegisterUser:
    return RegisterUser(
        user_repository=_user_repository,
        password_hasher=_password_hasher,
    )


def get_login_user_use_case() -> LoginUser:
    return LoginUser(
        user_repository=_user_repository,
        password_hasher=_password_hasher,
        token_service=_token_service,
    )
