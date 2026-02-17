from dataclasses import replace
from uuid import UUID

from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider


class InMemoryProviderCredentialRepository:
    """In-memory provider credential repository for testing."""

    def __init__(self) -> None:
        self._credentials: dict[UUID, UserModelProviderCredential] = {}

    async def save(self, credential: UserModelProviderCredential) -> None:
        self._credentials[credential.id] = credential

    async def list_by_user_id(self, user_id: UUID) -> list[UserModelProviderCredential]:
        return [
            credential
            for credential in self._credentials.values()
            if credential.user_id == user_id
        ]

    async def list_by_user_id_and_provider(
        self,
        user_id: UUID,
        provider: ModelProvider,
    ) -> list[UserModelProviderCredential]:
        return [
            credential
            for credential in self._credentials.values()
            if credential.user_id == user_id and credential.provider == provider
        ]

    async def set_active(self, credential_id: UUID, user_id: UUID) -> None:
        target = self._credentials.get(credential_id)
        if target is None or target.user_id != user_id:
            return

        provider = target.provider
        for existing_id, existing in self._credentials.items():
            if existing.user_id == user_id and existing.provider == provider:
                self._credentials[existing_id] = replace(existing, is_active=False)

        self._credentials[credential_id] = replace(target, is_active=True)

    async def delete(self, credential_id: UUID, user_id: UUID) -> None:
        credential = self._credentials.get(credential_id)
        if credential is None or credential.user_id != user_id:
            return
        del self._credentials[credential_id]
