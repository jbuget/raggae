from typing import Protocol
from uuid import UUID

from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider


class ProviderCredentialRepository(Protocol):
    """Interface for user model provider credential persistence."""

    async def save(self, credential: UserModelProviderCredential) -> None: ...

    async def list_by_user_id(self, user_id: UUID) -> list[UserModelProviderCredential]: ...

    async def list_by_user_id_and_provider(
        self,
        user_id: UUID,
        provider: ModelProvider,
    ) -> list[UserModelProviderCredential]: ...

    async def set_active(self, credential_id: UUID, user_id: UUID) -> None: ...

    async def set_inactive(self, credential_id: UUID, user_id: UUID) -> None: ...

    async def delete(self, credential_id: UUID, user_id: UUID) -> None: ...
