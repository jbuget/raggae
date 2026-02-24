import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.use_cases.provider_credentials.activate_provider_api_key import (
    ActivateProviderApiKey,
)
from raggae.application.use_cases.provider_credentials.delete_provider_api_key import (
    DeleteProviderApiKey,
)
from raggae.application.use_cases.provider_credentials.list_provider_api_keys import (
    ListProviderApiKeys,
)
from raggae.application.use_cases.provider_credentials.save_provider_api_key import (
    SaveProviderApiKey,
)
from raggae.domain.exceptions.provider_credential_exceptions import (
    DuplicateProviderCredentialError,
    ProviderCredentialNotFoundError,
)
from raggae.domain.exceptions.validation_errors import (
    InvalidModelProviderError,
    InvalidProviderApiKeyError,
)
from raggae.infrastructure.config.settings import settings
from raggae.presentation.api.dependencies import (
    get_activate_provider_api_key_use_case,
    get_current_user_id,
    get_delete_provider_api_key_use_case,
    get_list_provider_api_keys_use_case,
    get_save_provider_api_key_use_case,
)
from raggae.presentation.api.v1.schemas.model_credential_schemas import (
    ModelCredentialResponse,
    SaveModelCredentialRequest,
)

router = APIRouter(
    prefix="/model-credentials",
    tags=["model-credentials"],
    dependencies=[Depends(get_current_user_id)],
)
logger = logging.getLogger(__name__)


def _raise_if_user_provider_keys_disabled() -> None:
    if not settings.user_provider_keys_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )


@router.post("", status_code=status.HTTP_201_CREATED)
async def save_model_credential(
    data: SaveModelCredentialRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[SaveProviderApiKey, Depends(get_save_provider_api_key_use_case)],
) -> ModelCredentialResponse:
    _raise_if_user_provider_keys_disabled()
    try:
        credential = await use_case.execute(
            user_id=user_id,
            provider=data.provider,
            api_key=data.api_key,
        )
    except InvalidModelProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProviderApiKeyError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Invalid API key format",
        ) from None
    except DuplicateProviderCredentialError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This API key is already saved for this provider",
        ) from None

    logger.info(
        "provider_credential_saved",
        extra={
            "user_id": str(user_id),
            "provider": credential.provider,
            "credential_id": str(credential.id),
        },
    )

    return ModelCredentialResponse(
        id=credential.id,
        provider=credential.provider,
        masked_key=credential.masked_key,
        is_active=credential.is_active,
        created_at=credential.created_at,
        updated_at=credential.updated_at,
    )


@router.get("")
async def list_model_credentials(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListProviderApiKeys, Depends(get_list_provider_api_keys_use_case)],
) -> list[ModelCredentialResponse]:
    _raise_if_user_provider_keys_disabled()
    credentials = await use_case.execute(user_id=user_id)
    logger.info(
        "provider_credential_listed",
        extra={
            "user_id": str(user_id),
            "count": len(credentials),
        },
    )
    return [
        ModelCredentialResponse(
            id=item.id,
            provider=item.provider,
            masked_key=item.masked_key,
            is_active=item.is_active,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in credentials
    ]


@router.patch("/{credential_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def activate_model_credential(
    credential_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ActivateProviderApiKey, Depends(get_activate_provider_api_key_use_case)],
) -> None:
    _raise_if_user_provider_keys_disabled()
    try:
        await use_case.execute(credential_id=credential_id, user_id=user_id)
    except ProviderCredentialNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider credential not found",
        ) from None
    logger.info(
        "provider_credential_activated",
        extra={
            "user_id": str(user_id),
            "credential_id": str(credential_id),
        },
    )


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model_credential(
    credential_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeleteProviderApiKey, Depends(get_delete_provider_api_key_use_case)],
) -> None:
    _raise_if_user_provider_keys_disabled()
    await use_case.execute(credential_id=credential_id, user_id=user_id)
    logger.info(
        "provider_credential_deleted",
        extra={
            "user_id": str(user_id),
            "credential_id": str(credential_id),
        },
    )
