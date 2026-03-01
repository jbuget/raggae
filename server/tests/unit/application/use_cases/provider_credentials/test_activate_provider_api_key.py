from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.provider_credentials.activate_provider_api_key import (
    ActivateProviderApiKey,
)
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.exceptions.provider_credential_exceptions import (
    ProviderCredentialNotFoundError,
)
from raggae.domain.value_objects.model_provider import ModelProvider


class TestActivateProviderApiKey:
    async def test_activate_provider_api_key_success(self) -> None:
        # Given
        credential_id = uuid4()
        user_id = uuid4()
        now = datetime.now(UTC)
        repository = AsyncMock()
        repository.list_by_user_id.return_value = [
            UserModelProviderCredential(
                id=credential_id,
                user_id=user_id,
                provider=ModelProvider("gemini"),
                encrypted_api_key="enc",
                key_fingerprint="fp",
                key_suffix="9876",
                is_active=False,
                created_at=now,
                updated_at=now,
            )
        ]
        use_case = ActivateProviderApiKey(provider_credential_repository=repository)

        # When
        await use_case.execute(credential_id=credential_id, user_id=user_id)

        # Then
        repository.set_active.assert_awaited_once_with(credential_id, user_id)

    async def test_activate_provider_api_key_does_not_deactivate_other_credentials_of_same_provider(
        self,
    ) -> None:
        # Given — deux credentials pour le même provider, l'une inactive, l'autre active
        credential_id = uuid4()
        other_credential_id = uuid4()
        user_id = uuid4()
        now = datetime.now(UTC)
        repository = AsyncMock()
        repository.list_by_user_id.return_value = [
            UserModelProviderCredential(
                id=credential_id,
                user_id=user_id,
                provider=ModelProvider("openai"),
                encrypted_api_key="enc",
                key_fingerprint="fp1",
                key_suffix="1111",
                is_active=False,
                created_at=now,
                updated_at=now,
            ),
            UserModelProviderCredential(
                id=other_credential_id,
                user_id=user_id,
                provider=ModelProvider("openai"),
                encrypted_api_key="enc2",
                key_fingerprint="fp2",
                key_suffix="2222",
                is_active=True,
                created_at=now,
                updated_at=now,
            ),
        ]
        use_case = ActivateProviderApiKey(provider_credential_repository=repository)

        # When
        await use_case.execute(credential_id=credential_id, user_id=user_id)

        # Then — la clé est activée mais l'autre n'est PAS désactivée
        repository.set_active.assert_awaited_once_with(credential_id, user_id)
        repository.set_inactive.assert_not_awaited()

    async def test_activate_provider_api_key_not_owned_by_user_raises_error(self) -> None:
        # Given
        repository = AsyncMock()
        repository.list_by_user_id.return_value = []
        use_case = ActivateProviderApiKey(provider_credential_repository=repository)

        # When / Then
        with pytest.raises(ProviderCredentialNotFoundError):
            await use_case.execute(credential_id=uuid4(), user_id=uuid4())
