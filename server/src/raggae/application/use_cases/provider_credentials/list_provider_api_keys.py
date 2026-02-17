from uuid import UUID

from raggae.application.dto.provider_credential_dto import ProviderCredentialDTO
from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)


class ListProviderApiKeys:
    """Use case to list user provider API keys with masked values."""

    def __init__(self, provider_credential_repository: ProviderCredentialRepository) -> None:
        self._provider_credential_repository = provider_credential_repository

    async def execute(self, user_id: UUID) -> list[ProviderCredentialDTO]:
        credentials = await self._provider_credential_repository.list_by_user_id(user_id)
        return [
            ProviderCredentialDTO(
                id=credential.id,
                provider=credential.provider.value,
                masked_key=credential.masked_key,
                is_active=credential.is_active,
                created_at=credential.created_at,
                updated_at=credential.updated_at,
            )
            for credential in credentials
        ]
