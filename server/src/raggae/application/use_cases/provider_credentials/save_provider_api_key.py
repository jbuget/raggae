from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.provider_credential_dto import ProviderCredentialDTO
from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)
from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)
from raggae.application.interfaces.services.provider_api_key_validator import (
    ProviderApiKeyValidator,
)
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider


class SaveProviderApiKey:
    """Use case to persist a user provider API key securely."""

    def __init__(
        self,
        provider_credential_repository: ProviderCredentialRepository,
        provider_api_key_validator: ProviderApiKeyValidator,
        provider_api_key_crypto_service: ProviderApiKeyCryptoService,
    ) -> None:
        self._provider_credential_repository = provider_credential_repository
        self._provider_api_key_validator = provider_api_key_validator
        self._provider_api_key_crypto_service = provider_api_key_crypto_service

    async def execute(self, user_id: UUID, provider: str, api_key: str) -> ProviderCredentialDTO:
        model_provider = ModelProvider(provider)
        self._provider_api_key_validator.validate(model_provider, api_key)
        now = datetime.now(UTC)
        credential = UserModelProviderCredential(
            id=uuid4(),
            user_id=user_id,
            provider=model_provider,
            encrypted_api_key=self._provider_api_key_crypto_service.encrypt(api_key),
            key_fingerprint=self._provider_api_key_crypto_service.fingerprint(api_key),
            key_suffix=api_key[-4:],
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        await self._provider_credential_repository.save(credential)
        await self._provider_credential_repository.set_active(credential.id, user_id)
        return ProviderCredentialDTO(
            id=credential.id,
            provider=credential.provider.value,
            masked_key=credential.masked_key,
            is_active=True,
            created_at=credential.created_at,
            updated_at=credential.updated_at,
        )
