from uuid import UUID

from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)
from raggae.domain.exceptions.provider_credential_exceptions import (
    CredentialInUseError,
    ProviderCredentialNotFoundError,
)


class DeactivateProviderApiKey:
    """Use case to deactivate one provider API key for a user."""

    def __init__(
        self,
        provider_credential_repository: ProviderCredentialRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._provider_credential_repository = provider_credential_repository
        self._project_repository = project_repository

    async def execute(self, credential_id: UUID, user_id: UUID) -> None:
        credentials = await self._provider_credential_repository.list_by_user_id(user_id)
        if not any(credential.id == credential_id for credential in credentials):
            raise ProviderCredentialNotFoundError()

        projects = await self._project_repository.find_by_user_id(user_id)
        if any(
            p.embedding_api_key_credential_id == credential_id
            or p.llm_api_key_credential_id == credential_id
            for p in projects
        ):
            raise CredentialInUseError()

        await self._provider_credential_repository.set_inactive(credential_id, user_id)
