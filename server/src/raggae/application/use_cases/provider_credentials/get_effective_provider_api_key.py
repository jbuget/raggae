from uuid import UUID

from raggae.application.interfaces.repositories.provider_credential_repository import (
    ProviderCredentialRepository,
)
from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)
from raggae.domain.value_objects.model_provider import ModelProvider


class GetEffectiveProviderApiKey:
    """Resolve user provider API key, with fallback to global key."""

    def __init__(
        self,
        provider_credential_repository: ProviderCredentialRepository,
        provider_api_key_crypto_service: ProviderApiKeyCryptoService,
        global_api_keys: dict[str, str] | None = None,
    ) -> None:
        self._provider_credential_repository = provider_credential_repository
        self._provider_api_key_crypto_service = provider_api_key_crypto_service
        self._global_api_keys = global_api_keys or {}

    async def resolve(self, user_id: UUID, provider: str) -> str | None:
        model_provider = ModelProvider(provider)
        credentials = await self._provider_credential_repository.list_by_user_id_and_provider(
            user_id=user_id,
            provider=model_provider,
        )
        active_credential = next(
            (credential for credential in credentials if credential.is_active),
            None,
        )
        if active_credential is not None:
            return self._provider_api_key_crypto_service.decrypt(
                active_credential.encrypted_api_key
            )
        return self._global_api_keys.get(model_provider.value)
