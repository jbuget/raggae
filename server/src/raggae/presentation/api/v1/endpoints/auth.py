from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.use_cases.user.login_user import LoginUser
from raggae.application.use_cases.user.register_user import RegisterUser
from raggae.application.use_cases.user.get_current_user import GetCurrentUser
from raggae.application.use_cases.user.update_user_full_name import UpdateUserFullName
from raggae.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from raggae.presentation.api.dependencies import (
    get_current_user_id,
    get_current_user_use_case,
    get_login_user_use_case,
    get_register_user_use_case,
    get_update_user_full_name_use_case,
)
from raggae.presentation.api.v1.schemas.auth_schemas import (
    LoginUserRequest,
    RegisterUserRequest,
    TokenResponse,
    UpdateUserFullNameRequest,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterUserRequest,
    use_case: Annotated[RegisterUser, Depends(get_register_user_use_case)],
) -> UserResponse:
    try:
        user_dto = await use_case.execute(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
        )
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        ) from None
    return UserResponse(
        id=user_dto.id,
        email=user_dto.email,
        full_name=user_dto.full_name,
        is_active=user_dto.is_active,
        created_at=user_dto.created_at,
    )


@router.post("/login")
async def login(
    data: LoginUserRequest,
    use_case: Annotated[LoginUser, Depends(get_login_user_use_case)],
) -> TokenResponse:
    try:
        result = await use_case.execute(
            email=data.email,
            password=data.password,
        )
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        ) from None
    return TokenResponse(
        access_token=result.access_token,
        token_type=result.token_type,
    )


@router.get("/me", dependencies=[Depends(get_current_user_id)])
async def get_current_user(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetCurrentUser, Depends(get_current_user_use_case)],
) -> UserResponse:
    try:
        user_dto = await use_case.execute(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    return UserResponse(
        id=user_dto.id,
        email=user_dto.email,
        full_name=user_dto.full_name,
        is_active=user_dto.is_active,
        created_at=user_dto.created_at,
    )


@router.patch("/me/full-name", dependencies=[Depends(get_current_user_id)])
async def update_user_full_name(
    data: UpdateUserFullNameRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[
        UpdateUserFullName, Depends(get_update_user_full_name_use_case)
    ],
) -> UserResponse:
    try:
        user_dto = await use_case.execute(user_id=user_id, full_name=data.full_name)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    return UserResponse(
        id=user_dto.id,
        email=user_dto.email,
        full_name=user_dto.full_name,
        is_active=user_dto.is_active,
        created_at=user_dto.created_at,
    )
