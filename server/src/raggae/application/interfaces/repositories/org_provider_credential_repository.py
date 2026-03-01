from typing import Protocol
from uuid import UUID

from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider


class OrgProviderCredentialRepository(Protocol):
    """Interface for organization model provider credential persistence."""

    async def save(self, credential: OrgModelProviderCredential) -> None: ...

    async def list_by_org_id(self, organization_id: UUID) -> list[OrgModelProviderCredential]: ...

    async def list_by_org_id_and_provider(
        self,
        organization_id: UUID,
        provider: ModelProvider,
    ) -> list[OrgModelProviderCredential]: ...

    async def set_active(self, credential_id: UUID, organization_id: UUID) -> None: ...

    async def set_inactive(self, credential_id: UUID, organization_id: UUID) -> None: ...

    async def delete(self, credential_id: UUID, organization_id: UUID) -> None: ...
