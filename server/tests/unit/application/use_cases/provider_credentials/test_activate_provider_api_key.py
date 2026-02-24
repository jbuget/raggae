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

    async def test_activate_provider_api_key_not_owned_by_user_raises_error(self) -> None:
        # Given
        repository = AsyncMock()
        repository.list_by_user_id.return_value = []
        use_case = ActivateProviderApiKey(provider_credential_repository=repository)

        # When / Then
        with pytest.raises(ProviderCredentialNotFoundError):
            await use_case.execute(credential_id=uuid4(), user_id=uuid4())
