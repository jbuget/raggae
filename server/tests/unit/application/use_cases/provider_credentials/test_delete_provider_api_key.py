from unittest.mock import AsyncMock
from uuid import uuid4

from raggae.application.use_cases.provider_credentials.delete_provider_api_key import (
    DeleteProviderApiKey,
)


class TestDeleteProviderApiKey:
    async def test_delete_provider_api_key_calls_repository_with_user_scope(self) -> None:
        # Given
        repository = AsyncMock()
        use_case = DeleteProviderApiKey(provider_credential_repository=repository)
        credential_id = uuid4()
        user_id = uuid4()

        # When
        await use_case.execute(credential_id=credential_id, user_id=user_id)

        # Then
        repository.delete.assert_awaited_once_with(credential_id, user_id)
