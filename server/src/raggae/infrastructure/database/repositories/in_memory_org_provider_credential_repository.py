from dataclasses import replace
from uuid import UUID

from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider


class InMemoryOrgProviderCredentialRepository:
    """In-memory org provider credential repository for testing."""

    def __init__(self) -> None:
        self._credentials: dict[UUID, OrgModelProviderCredential] = {}

    async def save(self, credential: OrgModelProviderCredential) -> None:
        self._credentials[credential.id] = credential

    async def list_by_org_id(self, organization_id: UUID) -> list[OrgModelProviderCredential]:
        return [c for c in self._credentials.values() if c.organization_id == organization_id]

    async def list_by_org_id_and_provider(
        self,
        organization_id: UUID,
        provider: ModelProvider,
    ) -> list[OrgModelProviderCredential]:
        return [
            c
            for c in self._credentials.values()
            if c.organization_id == organization_id and c.provider == provider
        ]

    async def set_active(self, credential_id: UUID, organization_id: UUID) -> None:
        target = self._credentials.get(credential_id)
        if target is None or target.organization_id != organization_id:
            return
        self._credentials[credential_id] = replace(target, is_active=True)

    async def set_inactive(self, credential_id: UUID, organization_id: UUID) -> None:
        target = self._credentials.get(credential_id)
        if target is None or target.organization_id != organization_id:
            return
        self._credentials[credential_id] = replace(target, is_active=False)

    async def delete(self, credential_id: UUID, organization_id: UUID) -> None:
        credential = self._credentials.get(credential_id)
        if credential is None or credential.organization_id != organization_id:
            return
        del self._credentials[credential_id]
