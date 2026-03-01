from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from raggae.application.use_cases.project.update_project import UpdateProject
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.entities.project import Project
from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectChatHistoryMaxCharsError,
    InvalidProjectChatHistoryWindowSizeError,
    InvalidProjectEmbeddingBackendError,
    InvalidProjectEmbeddingModelError,
    InvalidProjectLLMBackendError,
    InvalidProjectLLMModelError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRerankerCandidateMultiplierError,
    InvalidProjectRetrievalMinScoreError,
    ProjectAPIKeyNotOwnedError,
    ProjectNotFoundError,
    ProjectSystemPromptTooLongError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class TestUpdateProject:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_provider_credential_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_organization_member_repository(self) -> AsyncMock:
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
        mock_organization_member_repository: AsyncMock,
        mock_provider_credential_repository: AsyncMock,
        mock_crypto_service: Mock,
    ) -> UpdateProject:
        return UpdateProject(
            project_repository=mock_project_repository,
            organization_member_repository=mock_organization_member_repository,
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

    async def test_update_project_for_org_owner_is_allowed(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = (
            OrganizationMember(
                id=uuid4(),
                organization_id=organization_id,
                user_id=requester_id,
                role=OrganizationMemberRole.OWNER,
                joined_at=datetime.now(UTC),
            )
        )

        result = await use_case.execute(
            project_id=project.id,
            user_id=requester_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
        )

        assert result.name == "New name"

    async def test_update_project_for_org_maker_is_allowed(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = (
            OrganizationMember(
                id=uuid4(),
                organization_id=organization_id,
                user_id=requester_id,
                role=OrganizationMemberRole.MAKER,
                joined_at=datetime.now(UTC),
            )
        )

        result = await use_case.execute(
            project_id=project.id,
            user_id=requester_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
        )

        assert result.name == "New name"

    async def test_update_project_for_org_user_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
        mock_organization_member_repository: AsyncMock,
    ) -> None:
        organization_id = uuid4()
        requester_id = uuid4()
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            organization_id=organization_id,
            name="Owner name",
            description="Owner description",
            system_prompt="Owner prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project
        mock_organization_member_repository.find_by_organization_and_user.return_value = (
            OrganizationMember(
                id=uuid4(),
                organization_id=organization_id,
                user_id=requester_id,
                role=OrganizationMemberRole.USER,
                joined_at=datetime.now(UTC),
            )
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project.id,
                user_id=requester_id,
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

    async def test_update_project_updates_retrieval_strategy_when_provided(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        result = await use_case.execute(
            project_id=project.id,
            user_id=project.user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
            retrieval_strategy="vector",
        )

        assert result.retrieval_strategy == "vector"

    async def test_update_project_updates_retrieval_top_k_when_provided(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        result = await use_case.execute(
            project_id=project.id,
            user_id=project.user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
            retrieval_top_k=14,
        )

        assert result.retrieval_top_k == 14

    async def test_update_project_updates_retrieval_min_score_when_provided(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        result = await use_case.execute(
            project_id=project.id,
            user_id=project.user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
            retrieval_min_score=0.55,
        )

        assert result.retrieval_min_score == 0.55

    async def test_update_project_updates_chat_history_settings_when_provided(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        result = await use_case.execute(
            project_id=project.id,
            user_id=project.user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
            chat_history_window_size=16,
            chat_history_max_chars=5000,
        )

        assert result.chat_history_window_size == 16
        assert result.chat_history_max_chars == 5000

    async def test_update_project_updates_reranker_settings_when_provided(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        result = await use_case.execute(
            project_id=project.id,
            user_id=project.user_id,
            name="New name",
            description="New description",
            system_prompt="New prompt",
            reranking_enabled=True,
            reranker_backend="cross_encoder",
            reranker_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            reranker_candidate_multiplier=5,
        )

        assert result.reranking_enabled is True
        assert result.reranker_backend == "cross_encoder"
        assert result.reranker_model == "cross-encoder/ms-marco-MiniLM-L-6-v2"
        assert result.reranker_candidate_multiplier == 5

    async def test_update_project_with_invalid_retrieval_min_score_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        with pytest.raises(InvalidProjectRetrievalMinScoreError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
                retrieval_min_score=-0.1,
            )

    async def test_update_project_with_invalid_chat_history_window_size_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        with pytest.raises(InvalidProjectChatHistoryWindowSizeError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
                chat_history_window_size=100,
            )

    async def test_update_project_with_invalid_chat_history_max_chars_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        with pytest.raises(InvalidProjectChatHistoryMaxCharsError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
                chat_history_max_chars=64,
            )

    async def test_update_project_with_invalid_reranker_backend_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        with pytest.raises(InvalidProjectRerankerBackendError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
                reranker_backend="unsupported",
            )

    async def test_update_project_with_invalid_reranker_multiplier_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Old name",
            description="Old description",
            system_prompt="Old prompt",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        with pytest.raises(InvalidProjectRerankerCandidateMultiplierError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="New name",
                description="New description",
                system_prompt="New prompt",
                reranker_candidate_multiplier=12,
            )

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

    async def test_update_project_with_invalid_llm_model_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="My project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When / Then
        with pytest.raises(InvalidProjectLLMModelError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="My project",
                description="",
                system_prompt="",
                llm_backend="gemini",
                llm_model="gemini-3-pro",
            )

    async def test_update_project_with_valid_llm_model_succeeds(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="My project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When
        result = await use_case.execute(
            project_id=project.id,
            user_id=project.user_id,
            name="My project",
            description="",
            system_prompt="",
            llm_backend="gemini",
            llm_model="gemini-3-flash-preview",
        )

        # Then
        assert result.llm_model == "gemini-3-flash-preview"

    async def test_update_project_with_empty_llm_model_skips_validation(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="My project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When — empty model means "use default", no validation
        result = await use_case.execute(
            project_id=project.id,
            user_id=project.user_id,
            name="My project",
            description="",
            system_prompt="",
            llm_backend="gemini",
            llm_model="",
        )

        # Then
        assert result.llm_model == ""

    async def test_update_project_ollama_llm_model_skips_validation(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given — Ollama allows arbitrary model names (user-installed)
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="My project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When
        result = await use_case.execute(
            project_id=project.id,
            user_id=project.user_id,
            name="My project",
            description="",
            system_prompt="",
            llm_backend="ollama",
            llm_model="any-custom-model:latest",
        )

        # Then
        assert result.llm_model == "any-custom-model:latest"

    async def test_update_project_with_invalid_embedding_model_raises_error(
        self,
        use_case: UpdateProject,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="My project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_project_repository.find_by_id.return_value = project

        # When / Then
        with pytest.raises(InvalidProjectEmbeddingModelError):
            await use_case.execute(
                project_id=project.id,
                user_id=project.user_id,
                name="My project",
                description="",
                system_prompt="",
                embedding_backend="openai",
                embedding_model="text-embedding-99-ultra",
            )
