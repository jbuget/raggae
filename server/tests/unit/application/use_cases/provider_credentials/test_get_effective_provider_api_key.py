from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from raggae.application.use_cases.provider_credentials.get_effective_provider_api_key import (
    GetEffectiveProviderApiKey,
)
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider


class TestGetEffectiveProviderApiKey:
    async def test_resolve_prefers_user_active_key(self) -> None:
        # Given
        user_id = uuid4()
        repository = AsyncMock()
        crypto_service = Mock()
        repository.list_by_user_id_and_provider.return_value = [
            UserModelProviderCredential(
                id=uuid4(),
                user_id=user_id,
                provider=ModelProvider("openai"),
                encrypted_api_key="enc-user-key",
                key_fingerprint="fp",
                key_suffix="1234",
                is_active=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]
        crypto_service.decrypt.return_value = "sk-user-1234"
        use_case = GetEffectiveProviderApiKey(
            provider_credential_repository=repository,
            provider_api_key_crypto_service=crypto_service,
            global_api_keys={"openai": "sk-global"},
        )

        # When
        result = await use_case.resolve(user_id=user_id, provider="openai")

        # Then
        assert result == "sk-user-1234"

    async def test_resolve_falls_back_to_global_key_when_user_key_missing(self) -> None:
        # Given
        repository = AsyncMock()
        repository.list_by_user_id_and_provider.return_value = []
        use_case = GetEffectiveProviderApiKey(
            provider_credential_repository=repository,
            provider_api_key_crypto_service=Mock(),
            global_api_keys={"gemini": "AIza-global"},
        )

        # When
        result = await use_case.resolve(user_id=uuid4(), provider="gemini")

        # Then
        assert result == "AIza-global"
