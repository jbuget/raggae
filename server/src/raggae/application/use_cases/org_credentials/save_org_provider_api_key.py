from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.org_provider_credential_dto import OrgProviderCredentialDTO
from raggae.application.interfaces.repositories.org_provider_credential_repository import (
    OrgProviderCredentialRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)
from raggae.application.interfaces.services.provider_api_key_validator import (
    ProviderApiKeyValidator,
)
from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.provider_credential_exceptions import OrgDuplicateCredentialError
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class SaveOrgProviderApiKey:
    """Use case to persist an organization provider API key securely."""

    def __init__(
        self,
        org_credential_repository: OrgProviderCredentialRepository,
        organization_member_repository: OrganizationMemberRepository,
        provider_api_key_validator: ProviderApiKeyValidator,
        provider_api_key_crypto_service: ProviderApiKeyCryptoService,
    ) -> None:
        self._org_credential_repository = org_credential_repository
        self._organization_member_repository = organization_member_repository
        self._provider_api_key_validator = provider_api_key_validator
        self._provider_api_key_crypto_service = provider_api_key_crypto_service

    async def execute(
        self, organization_id: UUID, user_id: UUID, provider: str, api_key: str
    ) -> OrgProviderCredentialDTO:
        model_provider = ModelProvider(provider)
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None or member.role not in {
            OrganizationMemberRole.OWNER,
            OrganizationMemberRole.MAKER,
        }:
            raise OrganizationAccessDeniedError(
                f"User {user_id} cannot manage credentials for organization {organization_id}"
            )
        self._provider_api_key_validator.validate(model_provider, api_key)
        fingerprint = self._provider_api_key_crypto_service.fingerprint(api_key)
        existing = await self._org_credential_repository.list_by_org_id_and_provider(
            organization_id, model_provider
        )
        if any(c.key_fingerprint == fingerprint for c in existing):
            raise OrgDuplicateCredentialError()
        now = datetime.now(UTC)
        credential = OrgModelProviderCredential(
            id=uuid4(),
            organization_id=organization_id,
            provider=model_provider,
            encrypted_api_key=self._provider_api_key_crypto_service.encrypt(api_key),
            key_fingerprint=fingerprint,
            key_suffix=api_key[-4:],
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        await self._org_credential_repository.save(credential)
        return OrgProviderCredentialDTO(
            id=credential.id,
            organization_id=credential.organization_id,
            provider=credential.provider.value,
            masked_key=credential.masked_key,
            is_active=credential.is_active,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
        )
