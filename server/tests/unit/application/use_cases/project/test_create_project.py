from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.use_cases.project.create_project import CreateProject
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    ProjectAPIKeyNotOwnedError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.model_provider import ModelProvider


class TestCreateProject:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_provider_credential_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_crypto_service(self) -> Mock:
        crypto = Mock()
        crypto.encrypt.side_effect = lambda value: f"enc:{value}"
        crypto.decrypt.side_effect = lambda value: value.removeprefix("enc:")
        crypto.fingerprint.side_effect = lambda value: f"fp:{value}"
        return crypto

    @pytest.fixture
    def use_case(
        self,
        mock_project_repository: AsyncMock,
        mock_provider_credential_repository: AsyncMock,
        mock_crypto_service: Mock,
    ) -> CreateProject:
        return CreateProject(
            project_repository=mock_project_repository,
            provider_credential_repository=mock_provider_credential_repository,
        ).with_crypto_service(mock_crypto_service)

    async def test_create_project_success(
        self,
        use_case: CreateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()

        # When
        result = await use_case.execute(
            user_id=user_id,
            name="My Project",
            description="A test project",
            system_prompt="You are a helpful assistant",
        )

        # Then
        assert result.name == "My Project"
        assert result.description == "A test project"
        assert result.system_prompt == "You are a helpful assistant"
        assert result.user_id == user_id
        assert result.is_published is False
        mock_project_repository.save.assert_called_once()

    async def test_create_project_with_ingestion_settings(
        self,
        use_case: CreateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()

        # When
        result = await use_case.execute(
            user_id=user_id,
            name="My Project",
            description="A test project",
            system_prompt="You are a helpful assistant",
            chunking_strategy=ChunkingStrategy.SEMANTIC,
            parent_child_chunking=True,
        )

        # Then
        assert result.chunking_strategy == ChunkingStrategy.SEMANTIC
        assert result.parent_child_chunking is True
        mock_project_repository.save.assert_called_once()

    async def test_create_project_with_too_long_system_prompt_raises(
        self,
        use_case: CreateProject,
    ) -> None:
        # Given
        # When / Then
        with pytest.raises(ProjectSystemPromptTooLongError):
            await use_case.execute(
                user_id=uuid4(),
                name="My Project",
                description="A test project",
                system_prompt="x" * 8001,
            )

    async def test_create_project_with_invalid_embedding_backend_raises(
        self,
        use_case: CreateProject,
    ) -> None:
        with pytest.raises(InvalidProjectEmbeddingBackendError):
            await use_case.execute(
                user_id=uuid4(),
                name="My Project",
                description="A test project",
                system_prompt="ok",
                embedding_backend="unsupported",
            )

    async def test_create_project_with_invalid_llm_backend_raises(
        self,
        use_case: CreateProject,
    ) -> None:
        with pytest.raises(InvalidProjectLLMBackendError):
            await use_case.execute(
                user_id=uuid4(),
                name="My Project",
                description="A test project",
                system_prompt="ok",
                llm_backend="unsupported",
            )

    async def test_create_project_with_non_owned_api_key_raises(
        self,
        use_case: CreateProject,
        mock_provider_credential_repository: AsyncMock,
    ) -> None:
        mock_provider_credential_repository.list_by_user_id_and_provider.return_value = []

        with pytest.raises(ProjectAPIKeyNotOwnedError, match="not registered for this user"):
            await use_case.execute(
                user_id=uuid4(),
                name="My Project",
                description="A test project",
                system_prompt="ok",
                llm_backend="openai",
                llm_api_key="sk-user-1234",
            )

    async def test_create_project_with_owned_api_key_encrypts_and_succeeds(
        self,
        use_case: CreateProject,
        mock_provider_credential_repository: AsyncMock,
    ) -> None:
        user_id = uuid4()
        mock_provider_credential_repository.list_by_user_id_and_provider.return_value = [
            UserModelProviderCredential(
                id=uuid4(),
                user_id=user_id,
                provider=ModelProvider("openai"),
                encrypted_api_key="enc:sk-user-1234",
                key_fingerprint="fp:sk-user-1234",
                key_suffix="1234",
                is_active=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]

        result = await use_case.execute(
            user_id=user_id,
            name="My Project",
            description="A test project",
            system_prompt="ok",
            llm_backend="openai",
            llm_api_key="sk-user-1234",
        )

        assert result.llm_backend == "openai"
        assert result.llm_api_key_masked is not None

    async def test_create_project_with_credential_id_resolves_key_and_succeeds(
        self,
        use_case: CreateProject,
        mock_provider_credential_repository: AsyncMock,
    ) -> None:
        user_id = uuid4()
        credential_id = uuid4()
        mock_provider_credential_repository.list_by_user_id_and_provider.return_value = [
            UserModelProviderCredential(
                id=credential_id,
                user_id=user_id,
                provider=ModelProvider("openai"),
                encrypted_api_key="enc:sk-user-1234",
                key_fingerprint="fp:sk-user-1234",
                key_suffix="1234",
                is_active=True,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        ]

        result = await use_case.execute(
            user_id=user_id,
            name="My Project",
            description="A test project",
            system_prompt="ok",
            llm_backend="openai",
            llm_api_key_credential_id=credential_id,
        )

        assert result.llm_backend == "openai"
        assert result.llm_api_key_masked is not None
