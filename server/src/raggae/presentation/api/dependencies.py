from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from raggae.application.use_cases.project.create_project import CreateProject
from raggae.application.use_cases.project.delete_project import DeleteProject
from raggae.application.use_cases.project.get_project import GetProject
from raggae.application.use_cases.project.list_projects import ListProjects
from raggae.application.use_cases.user.login_user import LoginUser
from raggae.application.use_cases.user.register_user import RegisterUser
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from raggae.infrastructure.database.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from raggae.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher
from raggae.infrastructure.services.jwt_token_service import JwtTokenService

_user_repository = InMemoryUserRepository()
_project_repository = InMemoryProjectRepository()
_password_hasher = BcryptPasswordHasher()
_token_service = JwtTokenService(secret_key="dev-secret-key", algorithm="HS256")
_bearer = HTTPBearer(auto_error=False)


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


def get_create_project_use_case() -> CreateProject:
    return CreateProject(project_repository=_project_repository)


def get_get_project_use_case() -> GetProject:
    return GetProject(project_repository=_project_repository)


def get_list_projects_use_case() -> ListProjects:
    return ListProjects(project_repository=_project_repository)


def get_delete_project_use_case() -> DeleteProject:
    return DeleteProject(project_repository=_project_repository)


def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> UUID:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing access token",
        )

    user_id = _token_service.verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    return user_id
