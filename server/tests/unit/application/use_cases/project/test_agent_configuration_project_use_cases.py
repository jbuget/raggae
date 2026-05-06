from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.project.get_project_configuration import (
    GetProjectConfiguration,
)
from raggae.application.use_cases.project.update_project_configuration import (
    UpdateProjectConfiguration,
)
from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRetrievalStrategyError,
    ProjectNotFoundError,
)
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.infrastructure.database.repositories.in_memory_agent_configuration_repository import (
    InMemoryAgentConfigurationRepository,
)
from raggae.infrastructure.database.repositories.in_memory_project_repository import (
    InMemoryProjectRepository,
)


def _make_project(project_id=None, user_id=None):
    return Project(
        id=project_id or uuid4(),
        user_id=user_id or uuid4(),
        name="Test Project",
        description="A test project",
        system_prompt="You are a helpful assistant.",
        is_published=False,
        created_at=datetime.now(UTC),
    )


def _make_agent_config(owner_id, config_type=AgentConfigurationType.PROJECT, **kwargs):
    return AgentConfiguration(
        id=uuid4(),
        owner_id=owner_id,
        type=config_type,
        **kwargs,
    )


class TestGetProjectConfiguration:
    async def test_raises_not_found_when_project_missing(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = GetProjectConfiguration(project_repo, config_repo)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=uuid4(), user_id=uuid4())

    async def test_raises_not_found_when_project_belongs_to_different_user(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        project = _make_project()
        await project_repo.save(project)
        use_case = GetProjectConfiguration(project_repo, config_repo)

        # When / Then — different user_id from project.user_id
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, user_id=uuid4())

    async def test_returns_none_when_no_config_exists(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        use_case = GetProjectConfiguration(project_repo, config_repo)

        # When
        result = await use_case.execute(project_id=project.id, user_id=user_id)

        # Then
        assert result is None

    async def test_returns_dto_when_config_exists(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        await config_repo.save(
            _make_agent_config(project.id, llm_backend="openai", retrieval_strategy="hybrid")
        )
        use_case = GetProjectConfiguration(project_repo, config_repo)

        # When
        result = await use_case.execute(project_id=project.id, user_id=user_id)

        # Then
        assert result is not None
        assert result.owner_id == project.id
        assert result.type == AgentConfigurationType.PROJECT
        assert result.llm_backend == "openai"
        assert result.retrieval_strategy == "hybrid"


class TestUpdateProjectConfiguration:
    async def test_raises_not_found_when_project_missing(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=uuid4(), user_id=uuid4())

    async def test_raises_not_found_when_project_belongs_to_different_user(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        project = _make_project()
        await project_repo.save(project)
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When / Then — different user_id from project.user_id
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project.id, user_id=uuid4())

    async def test_raises_invalid_embedding_backend_error(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectEmbeddingBackendError):
            await use_case.execute(
                project_id=project.id, user_id=user_id, embedding_backend="unsupported_embed"
            )

    async def test_raises_invalid_llm_backend_error(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectLLMBackendError):
            await use_case.execute(project_id=project.id, user_id=user_id, llm_backend="unsupported_llm")

    async def test_raises_invalid_retrieval_strategy_error(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectRetrievalStrategyError):
            await use_case.execute(
                project_id=project.id, user_id=user_id, retrieval_strategy="unsupported_strategy"
            )

    async def test_raises_invalid_reranker_backend_error(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectRerankerBackendError):
            await use_case.execute(
                project_id=project.id, user_id=user_id, reranker_backend="unsupported_reranker"
            )

    async def test_creates_config_when_none_exists(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When
        result = await use_case.execute(
            project_id=project.id,
            user_id=user_id,
            llm_backend="anthropic",
            retrieval_strategy="vector",
            retrieval_top_k=10,
        )

        # Then
        assert result.owner_id == project.id
        assert result.type == AgentConfigurationType.PROJECT
        assert result.llm_backend == "anthropic"
        assert result.retrieval_strategy == "vector"
        assert result.retrieval_top_k == 10
        saved = await config_repo.find_by_owner(project.id, AgentConfigurationType.PROJECT)
        assert saved is not None
        assert saved.llm_backend == "anthropic"

    async def test_updates_config_and_preserves_id_when_config_already_exists(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        existing_config = _make_agent_config(project.id, llm_backend="ollama")
        await config_repo.save(existing_config)
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When
        result = await use_case.execute(
            project_id=project.id,
            user_id=user_id,
            llm_backend="openai",
        )

        # Then
        assert result.llm_backend == "openai"
        saved = await config_repo.find_by_owner(project.id, AgentConfigurationType.PROJECT)
        assert saved is not None
        assert saved.id == existing_config.id
        assert saved.llm_backend == "openai"

    async def test_saves_with_project_type(self) -> None:
        # Given
        project_repo = InMemoryProjectRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        user_id = uuid4()
        project = _make_project(user_id=user_id)
        await project_repo.save(project)
        use_case = UpdateProjectConfiguration(project_repo, config_repo)

        # When
        result = await use_case.execute(project_id=project.id, user_id=user_id)

        # Then
        assert result.type == AgentConfigurationType.PROJECT
        saved = await config_repo.find_by_owner(project.id, AgentConfigurationType.PROJECT)
        assert saved is not None
        assert saved.type == AgentConfigurationType.PROJECT
