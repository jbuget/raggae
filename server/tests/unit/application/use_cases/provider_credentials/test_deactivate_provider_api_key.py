from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.provider_credentials.deactivate_provider_api_key import (
    DeactivateProviderApiKey,
)
from raggae.domain.exceptions.provider_credential_exceptions import (
    CredentialInUseError,
    ProviderCredentialNotFoundError,
)


class TestDeactivateProviderApiKey:
    async def test_deactivate_provider_api_key_calls_set_inactive(self) -> None:
        # Given
        user_id = uuid4()
        credential_id = uuid4()
        credential_repo = AsyncMock()
        credential_repo.list_by_user_id = AsyncMock(
            return_value=[type("C", (), {"id": credential_id})()]
        )
        project_repo = AsyncMock()
        project_repo.find_by_user_id = AsyncMock(return_value=[])
        use_case = DeactivateProviderApiKey(
            provider_credential_repository=credential_repo,
            project_repository=project_repo,
        )

        # When
        await use_case.execute(credential_id=credential_id, user_id=user_id)

        # Then
        credential_repo.set_inactive.assert_awaited_once_with(credential_id, user_id)

    async def test_deactivate_provider_api_key_not_owned_raises_error(self) -> None:
        # Given
        user_id = uuid4()
        credential_repo = AsyncMock()
        credential_repo.list_by_user_id = AsyncMock(return_value=[])
        project_repo = AsyncMock()
        use_case = DeactivateProviderApiKey(
            provider_credential_repository=credential_repo,
            project_repository=project_repo,
        )

        # When / Then
        with pytest.raises(ProviderCredentialNotFoundError):
            await use_case.execute(credential_id=uuid4(), user_id=user_id)

    async def test_deactivate_provider_api_key_in_use_by_embedding_raises_error(self) -> None:
        # Given
        user_id = uuid4()
        credential_id = uuid4()
        credential_repo = AsyncMock()
        credential_repo.list_by_user_id = AsyncMock(
            return_value=[type("C", (), {"id": credential_id})()]
        )
        project = type(
            "P",
            (),
            {"embedding_api_key_credential_id": credential_id, "llm_api_key_credential_id": None},
        )()
        project_repo = AsyncMock()
        project_repo.find_by_user_id = AsyncMock(return_value=[project])
        use_case = DeactivateProviderApiKey(
            provider_credential_repository=credential_repo,
            project_repository=project_repo,
        )

        # When / Then
        with pytest.raises(CredentialInUseError):
            await use_case.execute(credential_id=credential_id, user_id=user_id)

    async def test_deactivate_provider_api_key_in_use_by_llm_raises_error(self) -> None:
        # Given
        user_id = uuid4()
        credential_id = uuid4()
        credential_repo = AsyncMock()
        credential_repo.list_by_user_id = AsyncMock(
            return_value=[type("C", (), {"id": credential_id})()]
        )
        project = type(
            "P",
            (),
            {"embedding_api_key_credential_id": None, "llm_api_key_credential_id": credential_id},
        )()
        project_repo = AsyncMock()
        project_repo.find_by_user_id = AsyncMock(return_value=[project])
        use_case = DeactivateProviderApiKey(
            provider_credential_repository=credential_repo,
            project_repository=project_repo,
        )

        # When / Then
        with pytest.raises(CredentialInUseError):
            await use_case.execute(credential_id=credential_id, user_id=user_id)
