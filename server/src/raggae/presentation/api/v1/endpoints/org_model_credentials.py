import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.use_cases.org_credentials.activate_org_provider_api_key import (
    ActivateOrgProviderApiKey,
)
from raggae.application.use_cases.org_credentials.deactivate_org_provider_api_key import (
    DeactivateOrgProviderApiKey,
)
from raggae.application.use_cases.org_credentials.delete_org_provider_api_key import (
    DeleteOrgProviderApiKey,
)
from raggae.application.use_cases.org_credentials.list_org_provider_api_keys import (
    ListOrgProviderApiKeys,
)
from raggae.application.use_cases.org_credentials.save_org_provider_api_key import (
    SaveOrgProviderApiKey,
)
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.provider_credential_exceptions import (
    OrgCredentialInUseError,
    OrgCredentialNotFoundError,
    OrgDuplicateCredentialError,
)
from raggae.domain.exceptions.validation_errors import (
    InvalidModelProviderError,
    InvalidProviderApiKeyError,
)
from raggae.presentation.api.dependencies import (
    get_activate_org_provider_api_key_use_case,
    get_current_user_id,
    get_deactivate_org_provider_api_key_use_case,
    get_delete_org_provider_api_key_use_case,
    get_list_org_provider_api_keys_use_case,
    get_save_org_provider_api_key_use_case,
)
from raggae.presentation.api.v1.schemas.org_model_credential_schemas import (
    OrgModelCredentialResponse,
    SaveOrgModelCredentialRequest,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/model-credentials",
    tags=["org-model-credentials"],
    dependencies=[Depends(get_current_user_id)],
)
logger = logging.getLogger(__name__)


@router.post("", status_code=status.HTTP_201_CREATED)
async def save_org_model_credential(
    organization_id: UUID,
    data: SaveOrgModelCredentialRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[SaveOrgProviderApiKey, Depends(get_save_org_provider_api_key_use_case)],
) -> OrgModelCredentialResponse:
    try:
        credential = await use_case.execute(
            organization_id=organization_id,
            user_id=user_id,
            provider=data.provider,
            api_key=data.api_key,
        )
    except OrganizationAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        ) from None
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
    except OrgDuplicateCredentialError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This API key is already saved for this provider",
        ) from None
    logger.info(
        "org_provider_credential_saved",
        extra={
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "provider": credential.provider,
            "credential_id": str(credential.id),
        },
    )
    return OrgModelCredentialResponse(
        id=credential.id,
        organization_id=credential.organization_id,
        provider=credential.provider,
        masked_key=credential.masked_key,
        is_active=credential.is_active,
        created_at=credential.created_at,
        updated_at=credential.updated_at,
    )


@router.get("")
async def list_org_model_credentials(
    organization_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListOrgProviderApiKeys, Depends(get_list_org_provider_api_keys_use_case)],
) -> list[OrgModelCredentialResponse]:
    try:
        credentials = await use_case.execute(organization_id=organization_id, user_id=user_id)
    except OrganizationAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        ) from None
    return [
        OrgModelCredentialResponse(
            id=item.id,
            organization_id=item.organization_id,
            provider=item.provider,
            masked_key=item.masked_key,
            is_active=item.is_active,
            created_at=item.created_at,
            updated_at=item.updated_at,
        )
        for item in credentials
    ]


@router.patch("/{credential_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def activate_org_model_credential(
    organization_id: UUID,
    credential_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[
        ActivateOrgProviderApiKey, Depends(get_activate_org_provider_api_key_use_case)
    ],
) -> None:
    try:
        await use_case.execute(
            credential_id=credential_id, organization_id=organization_id, user_id=user_id
        )
    except OrganizationAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        ) from None
    except OrgCredentialNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Org provider credential not found",
        ) from None
    logger.info(
        "org_provider_credential_activated",
        extra={
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "credential_id": str(credential_id),
        },
    )


@router.patch("/{credential_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_org_model_credential(
    organization_id: UUID,
    credential_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[
        DeactivateOrgProviderApiKey, Depends(get_deactivate_org_provider_api_key_use_case)
    ],
) -> None:
    try:
        await use_case.execute(
            credential_id=credential_id, organization_id=organization_id, user_id=user_id
        )
    except OrganizationAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        ) from None
    except OrgCredentialNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Org provider credential not found",
        ) from None
    except OrgCredentialInUseError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This API key is used by one or more projects and cannot be deactivated",
        ) from None
    logger.info(
        "org_provider_credential_deactivated",
        extra={
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "credential_id": str(credential_id),
        },
    )


@router.delete("/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org_model_credential(
    organization_id: UUID,
    credential_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeleteOrgProviderApiKey, Depends(get_delete_org_provider_api_key_use_case)],
) -> None:
    try:
        await use_case.execute(
            credential_id=credential_id, organization_id=organization_id, user_id=user_id
        )
    except OrganizationAccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        ) from None
    except OrgCredentialNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Org provider credential not found",
        ) from None
    except OrgCredentialInUseError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This API key is used by one or more projects and cannot be deleted",
        ) from None
    logger.info(
        "org_provider_credential_deleted",
        extra={
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "credential_id": str(credential_id),
        },
    )
