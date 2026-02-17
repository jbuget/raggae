from uuid import UUID

from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)


class DeleteProviderApiKey:
    """Use case to delete one provider API key for a user."""

    def __init__(self, provider_credential_repository: ProviderCredentialRepository) -> None:
        self._provider_credential_repository = provider_credential_repository

    async def execute(self, credential_id: UUID, user_id: UUID) -> None:
        await self._provider_credential_repository.delete(credential_id, user_id)
