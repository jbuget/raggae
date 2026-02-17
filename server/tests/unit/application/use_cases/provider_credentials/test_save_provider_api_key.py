from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.use_cases.provider_credentials.save_provider_api_key import (
    SaveProviderApiKey,
)
from raggae.domain.exceptions.validation_errors import InvalidModelProviderError


class TestSaveProviderApiKey:
    async def test_save_provider_api_key_success(self) -> None:
        # Given
        user_id = uuid4()
        repository = AsyncMock()
        validator = Mock()
        crypto_service = Mock()
        crypto_service.encrypt.return_value = "encrypted-key"
        crypto_service.fingerprint.return_value = "fingerprint"
        use_case = SaveProviderApiKey(
            provider_credential_repository=repository,
            provider_api_key_validator=validator,
            provider_api_key_crypto_service=crypto_service,
        )

        # When
        result = await use_case.execute(user_id=user_id, provider="openai", api_key="sk-test-abcd")

        # Then
        assert result.provider == "openai"
        assert result.masked_key == "...abcd"
        assert result.is_active is True
        validator.validate.assert_called_once()
        repository.save.assert_awaited_once()
        repository.set_active.assert_awaited_once_with(result.id, user_id)

    async def test_save_provider_api_key_invalid_provider_raises_error(self) -> None:
        # Given
        use_case = SaveProviderApiKey(
            provider_credential_repository=AsyncMock(),
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=Mock(),
        )

        # When / Then
        with pytest.raises(InvalidModelProviderError):
            await use_case.execute(user_id=uuid4(), provider="mistral", api_key="invalid")
