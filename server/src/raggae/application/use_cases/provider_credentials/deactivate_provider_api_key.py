from uuid import UUID

from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)
from raggae.domain.exceptions.provider_credential_exceptions import (
    ProviderCredentialNotFoundError,
)


class DeactivateProviderApiKey:
    """Use case to deactivate one provider API key for a user."""

    def __init__(self, provider_credential_repository: ProviderCredentialRepository) -> None:
        self._provider_credential_repository = provider_credential_repository

    async def execute(self, credential_id: UUID, user_id: UUID) -> None:
        credentials = await self._provider_credential_repository.list_by_user_id(user_id)
        if not any(credential.id == credential_id for credential in credentials):
            raise ProviderCredentialNotFoundError()
        await self._provider_credential_repository.set_inactive(credential_id, user_id)
