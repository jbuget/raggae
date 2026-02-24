from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from raggae.application.use_cases.project.update_project import UpdateProject
from raggae.domain.entities.project import Project
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    ProjectAPIKeyNotOwnedError,
    ProjectNotFoundError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.model_provider import ModelProvider


class TestUpdateProject:
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
    ) -> UpdateProject:
        return UpdateProject(
            project_repository=mock_project_repository,
            provider_credential_repository=mock_provider_credential_repository,
        ).with_crypto_service(mock_crypto_service)

    async def test_update_project_success(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        project = Project(
            id=project_id,
            user_id=user_id,
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
        )

        # Then
        assert result.id == project_id
        assert result.user_id == user_id
        assert result.name == "New name"
        assert result.description == "New description"
        assert result.system_prompt == "New prompt"
        mock_project_repository.save.assert_called_once()

    async def test_update_project_not_found_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=uuid4(),
                user_id=uuid4(),
                name="New name",
                description="New description",
                system_prompt="New prompt",
            )

    async def test_update_project_for_other_user_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project.id,
                user_id=uuid4(),
                name="New name",
                description="New description",
                system_prompt="New prompt",
            )

    async def test_update_project_updates_chunking_settings_when_provided(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        project = Project(
            id=project_id,
            user_id=user_id,
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
            chunking_strategy=ChunkingStrategy.SEMANTIC,
            parent_child_chunking=True,
        )

        # Then
        assert result.chunking_strategy == ChunkingStrategy.SEMANTIC
        assert result.parent_child_chunking is True

    async def test_update_project_with_too_long_system_prompt_raises_error(
        self,
        use_case: UpdateProject,
    ) -> None:
        # When / Then
        with pytest.raises(ProjectSystemPromptTooLongError):
            await use_case.execute(
                project_id=uuid4(),
                user_id=uuid4(),
                name="New name",
                description="New description",
                system_prompt="x" * 8001,
            )

    async def test_update_project_with_invalid_embedding_backend_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        with pytest.raises(InvalidProjectEmbeddingBackendError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
                embedding_backend="unsupported",
            )

    async def test_update_project_with_invalid_llm_backend_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        with pytest.raises(InvalidProjectLLMBackendError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
                llm_backend="unsupported",
            )

    async def test_update_project_with_non_owned_api_key_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_provider_credential_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_provider_credential_repository.list_by_user_id_and_provider.return_value = []

        with pytest.raises(ProjectAPIKeyNotOwnedError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
                llm_backend="openai",
                llm_api_key="sk-user-1234",
            )

    async def test_update_project_with_owned_api_key_succeeds(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_provider_credential_repository: AsyncMock,
    ) -> None:
        user_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=user_id,
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
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
            project_id=project.id,
            user_id=user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
            llm_backend="openai",
            llm_api_key="sk-user-1234",
        )

        assert result.llm_backend == "openai"

    async def test_update_project_with_credential_id_resolves_key_and_succeeds(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_provider_credential_repository: AsyncMock,
    ) -> None:
        user_id = uuid4()
        credential_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=user_id,
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
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
            project_id=project.id,
            user_id=user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
            llm_backend="openai",
            llm_api_key_credential_id=credential_id,
        )

        assert result.llm_backend == "openai"
        assert result.llm_api_key_credential_id == credential_id
