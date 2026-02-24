from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.provider_credentials.deactivate_provider_api_key import (
    DeactivateProviderApiKey,
)
from raggae.domain.exceptions.provider_credential_exceptions import (
    ProviderCredentialNotFoundError,
)


class TestDeactivateProviderApiKey:
    async def test_deactivate_provider_api_key_calls_set_inactive(self) -> None:
        # Given
        user_id = uuid4()
        credential_id = uuid4()
        repository = AsyncMock()
        repository.list_by_user_id = AsyncMock(
            return_value=[
                type("C", (), {"id": credential_id})(),
            ]
        )
        use_case = DeactivateProviderApiKey(provider_credential_repository=repository)

        # When
        await use_case.execute(credential_id=credential_id, user_id=user_id)

        # Then
        repository.set_inactive.assert_awaited_once_with(credential_id, user_id)

    async def test_deactivate_provider_api_key_not_owned_raises_error(self) -> None:
        # Given
        user_id = uuid4()
        repository = AsyncMock()
        repository.list_by_user_id = AsyncMock(return_value=[])
        use_case = DeactivateProviderApiKey(provider_credential_repository=repository)

        # When / Then
        with pytest.raises(ProviderCredentialNotFoundError):
            await use_case.execute(credential_id=uuid4(), user_id=user_id)
