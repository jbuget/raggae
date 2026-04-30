from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.use_cases.user.get_current_user import GetCurrentUser
from raggae.application.use_cases.user.get_user_project_defaults import GetUserProjectDefaults
from raggae.application.use_cases.user.login_user import LoginUser
from raggae.application.use_cases.user.register_user import RegisterUser
from raggae.application.use_cases.user.update_user_full_name import UpdateUserFullName
from raggae.application.use_cases.user.update_user_locale import UpdateUserLocale
from raggae.application.use_cases.user.upsert_user_project_defaults import UpsertUserProjectDefaults
from raggae.domain.exceptions.user_exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from raggae.domain.value_objects.locale import Locale
from raggae.presentation.api.dependencies import (
    get_current_user_id,
    get_current_user_use_case,
    get_get_user_project_defaults_use_case,
    get_login_user_use_case,
    get_register_user_use_case,
    get_update_user_full_name_use_case,
    get_update_user_locale_use_case,
    get_upsert_user_project_defaults_use_case,
)
from raggae.presentation.api.v1.schemas.auth_schemas import (
    LoginUserRequest,
    RegisterUserRequest,
    TokenResponse,
    UpdateUserFullNameRequest,
    UpdateUserLocaleRequest,
    UpsertUserProjectDefaultsRequest,
    UserProjectDefaultsResponse,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_response(user_dto) -> UserResponse:  # type: ignore[no-untyped-def]
    return UserResponse(
        id=user_dto.id,
        email=user_dto.email,
        full_name=user_dto.full_name,
        is_active=user_dto.is_active,
        created_at=user_dto.created_at,
        locale=str(user_dto.locale),
    )


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
    return _user_response(user_dto)


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
    return _user_response(user_dto)


@router.patch("/me/full-name", dependencies=[Depends(get_current_user_id)])
async def update_user_full_name(
    data: UpdateUserFullNameRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateUserFullName, Depends(get_update_user_full_name_use_case)],
) -> UserResponse:
    try:
        user_dto = await use_case.execute(user_id=user_id, full_name=data.full_name)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    return _user_response(user_dto)


@router.patch("/me/locale", dependencies=[Depends(get_current_user_id)])
async def update_user_locale(
    data: UpdateUserLocaleRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateUserLocale, Depends(get_update_user_locale_use_case)],
) -> UserResponse:
    try:
        user_dto = await use_case.execute(user_id=user_id, locale=Locale(data.locale))
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    return _user_response(user_dto)


@router.get("/me/project-defaults", dependencies=[Depends(get_current_user_id)])
async def get_user_project_defaults(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetUserProjectDefaults, Depends(get_get_user_project_defaults_use_case)],
) -> UserProjectDefaultsResponse | None:
    try:
        result = await use_case.execute(user_id=user_id)
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    if result is None:
        return None
    return UserProjectDefaultsResponse.from_dto(result)


@router.put("/me/project-defaults", dependencies=[Depends(get_current_user_id)])
async def upsert_user_project_defaults(
    data: UpsertUserProjectDefaultsRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpsertUserProjectDefaults, Depends(get_upsert_user_project_defaults_use_case)],
) -> UserProjectDefaultsResponse:
    try:
        result = await use_case.execute(
            user_id=user_id,
            embedding_backend=data.embedding_backend,
            embedding_model=data.embedding_model,
            embedding_api_key_credential_id=data.embedding_api_key_credential_id,
            llm_backend=data.llm_backend,
            llm_model=data.llm_model,
            llm_api_key_credential_id=data.llm_api_key_credential_id,
            chunking_strategy=data.chunking_strategy,
            parent_child_chunking=data.parent_child_chunking,
            retrieval_strategy=data.retrieval_strategy,
            retrieval_top_k=data.retrieval_top_k,
            retrieval_min_score=data.retrieval_min_score,
            reranking_enabled=data.reranking_enabled,
            reranker_backend=data.reranker_backend,
            reranker_model=data.reranker_model,
            reranker_candidate_multiplier=data.reranker_candidate_multiplier,
            chat_history_window_size=data.chat_history_window_size,
            chat_history_max_chars=data.chat_history_max_chars,
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from None
    return UserProjectDefaultsResponse.from_dto(result)
