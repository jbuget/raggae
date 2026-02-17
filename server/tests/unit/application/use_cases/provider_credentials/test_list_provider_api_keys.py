from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from raggae.application.use_cases.provider_credentials.list_provider_api_keys import (
    ListProviderApiKeys,
)
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider


class TestListProviderApiKeys:
    async def test_list_provider_api_keys_returns_masked_credentials(self) -> None:
        # Given
        user_id = uuid4()
        repository = AsyncMock()
        repository.list_by_user_id.return_value = [
            UserModelProviderCredential(
                id=uuid4(),
                user_id=user_id,
                provider=ModelProvider("anthropic"),
                encrypted_api_key="enc",
                key_fingerprint="fp",
                key_suffix="1234",
                is_active=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]
        use_case = ListProviderApiKeys(provider_credential_repository=repository)

        # When
        result = await use_case.execute(user_id=user_id)

        # Then
        assert len(result) == 1
        assert result[0].provider == "anthropic"
        assert result[0].masked_key == "...1234"
