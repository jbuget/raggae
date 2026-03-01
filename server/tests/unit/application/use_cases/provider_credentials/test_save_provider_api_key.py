from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.use_cases.provider_credentials.save_provider_api_key import (
    SaveProviderApiKey,
)
from raggae.domain.exceptions.provider_credential_exceptions import (
    DuplicateProviderCredentialError,
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
        repository.set_active.assert_not_awaited()

    async def test_save_provider_api_key_credential_saved_active_directly(self) -> None:
        # Given
        user_id = uuid4()
        saved_credentials: list = []

        async def capture_save(credential: object) -> None:
            saved_credentials.append(credential)

        repository = AsyncMock()
        repository.save = AsyncMock(side_effect=capture_save)
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
        result = await use_case.execute(user_id=user_id, provider="gemini", api_key="AIzatest1234")

        # Then — la credential est directement insérée active (plus de contrainte d'unicité)
        assert len(saved_credentials) == 1
        assert saved_credentials[0].is_active is True
        repository.set_active.assert_not_awaited()
        assert result.is_active is True

    async def test_save_provider_api_key_duplicate_fingerprint_raises_error(self) -> None:
        # Given — an existing credential with the same fingerprint
        from datetime import UTC, datetime

        from raggae.domain.entities.user_model_provider_credential import (
            UserModelProviderCredential,
        )
        from raggae.domain.value_objects.model_provider import ModelProvider

        user_id = uuid4()
        existing = UserModelProviderCredential(
            id=uuid4(),
            user_id=user_id,
            provider=ModelProvider("gemini"),
            encrypted_api_key="enc",
            key_fingerprint="same-fingerprint",
            key_suffix="1234",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        repository = AsyncMock()
        repository.list_by_user_id_and_provider = AsyncMock(return_value=[existing])
        crypto_service = Mock()
        crypto_service.fingerprint.return_value = "same-fingerprint"
        crypto_service.encrypt.return_value = "encrypted"
        use_case = SaveProviderApiKey(
            provider_credential_repository=repository,
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=crypto_service,
        )

        # When / Then
        with pytest.raises(DuplicateProviderCredentialError):
            await use_case.execute(user_id=user_id, provider="gemini", api_key="AIzatest1234")

    async def test_save_provider_api_key_does_not_deactivate_existing_credentials(self) -> None:
        # Given — une credential active existante pour le même provider
        from datetime import UTC, datetime

        from raggae.domain.entities.user_model_provider_credential import (
            UserModelProviderCredential,
        )
        from raggae.domain.value_objects.model_provider import ModelProvider

        user_id = uuid4()
        existing = UserModelProviderCredential(
            id=uuid4(),
            user_id=user_id,
            provider=ModelProvider("openai"),
            encrypted_api_key="enc",
            key_fingerprint="other-fingerprint",
            key_suffix="1111",
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        repository = AsyncMock()
        repository.list_by_user_id_and_provider = AsyncMock(return_value=[existing])
        crypto_service = Mock()
        crypto_service.fingerprint.return_value = "new-fingerprint"
        crypto_service.encrypt.return_value = "encrypted"
        use_case = SaveProviderApiKey(
            provider_credential_repository=repository,
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=crypto_service,
        )

        # When
        await use_case.execute(user_id=user_id, provider="openai", api_key="sk-test-xxxx")

        # Then — les credentials existantes ne sont PAS désactivées
        repository.set_inactive.assert_not_awaited()
        repository.save.assert_awaited_once()

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
