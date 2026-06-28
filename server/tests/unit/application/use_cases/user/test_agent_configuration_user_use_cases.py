from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.user.get_user_agent_configuration import (
    GetUserAgentConfiguration,
)
from raggae.application.use_cases.user.upsert_user_agent_configuration import (
    UpsertUserAgentConfiguration,
)
from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.entities.user import User
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRetrievalStrategyError,
)
from raggae.domain.exceptions.user_exceptions import UserNotFoundError
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.domain.value_objects.locale import Locale
from raggae.infrastructure.database.repositories.in_memory_agent_configuration_repository import (
    InMemoryAgentConfigurationRepository,
)
from raggae.infrastructure.database.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


def _make_user(user_id=None):
    return User(
        id=user_id or uuid4(),
        email="user@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True,
        created_at=datetime.now(UTC),
        locale=Locale.EN,
    )


def _make_agent_config(owner_id, config_type=AgentConfigurationType.USER, **kwargs):
    return AgentConfiguration(
        id=uuid4(),
        owner_id=owner_id,
        owner_type=config_type,
        **kwargs,
    )


class TestGetUserAgentConfiguration:
    async def test_raises_not_found_when_user_missing(self) -> None:
        # Given
        user_repo = InMemoryUserRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = GetUserAgentConfiguration(user_repo, config_repo)

        # When / Then
        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id=uuid4())

    async def test_returns_none_when_no_config_exists(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = GetUserAgentConfiguration(user_repo, config_repo)

        # When
        result = await use_case.execute(user_id=user.id)

        # Then
        assert result is None

    async def test_returns_dto_when_config_exists(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        await config_repo.save(
            _make_agent_config(user.id, llm_backend="anthropic", embedding_backend="openai")
        )
        use_case = GetUserAgentConfiguration(user_repo, config_repo)

        # When
        result = await use_case.execute(user_id=user.id)

        # Then
        assert result is not None
        assert result.owner_id == user.id
        assert result.owner_type == AgentConfigurationType.USER
        assert result.llm_backend == "anthropic"
        assert result.embedding_backend == "openai"


class TestUpsertUserAgentConfiguration:
    async def test_raises_not_found_when_user_missing(self) -> None:
        # Given
        user_repo = InMemoryUserRepository()
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpsertUserAgentConfiguration(user_repo, config_repo)

        # When / Then
        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id=uuid4())

    async def test_raises_invalid_embedding_backend_error(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpsertUserAgentConfiguration(user_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectEmbeddingBackendError):
            await use_case.execute(user_id=user.id, embedding_backend="unsupported_embed")

    async def test_raises_invalid_llm_backend_error(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpsertUserAgentConfiguration(user_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectLLMBackendError):
            await use_case.execute(user_id=user.id, llm_backend="unsupported_llm")

    async def test_raises_invalid_retrieval_strategy_error(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpsertUserAgentConfiguration(user_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectRetrievalStrategyError):
            await use_case.execute(user_id=user.id, retrieval_strategy="unsupported_strategy")

    async def test_raises_invalid_reranker_backend_error(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpsertUserAgentConfiguration(user_repo, config_repo)

        # When / Then
        with pytest.raises(InvalidProjectRerankerBackendError):
            await use_case.execute(user_id=user.id, reranker_backend="unsupported_reranker")

    async def test_creates_config_when_none_exists(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpsertUserAgentConfiguration(user_repo, config_repo)

        # When
        result = await use_case.execute(
            user_id=user.id,
            llm_backend="openai",
            llm_model="gpt-4.1",
            embedding_backend="openai",
        )

        # Then
        assert result.owner_id == user.id
        assert result.owner_type == AgentConfigurationType.USER
        assert result.llm_backend == "openai"
        assert result.llm_model == "gpt-4.1"
        assert result.embedding_backend == "openai"
        saved = await config_repo.find_by_owner(user.id, AgentConfigurationType.USER)
        assert saved is not None
        assert saved.llm_backend == "openai"

    async def test_updates_config_and_preserves_id_when_config_already_exists(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        existing_config = _make_agent_config(user.id, llm_backend="ollama")
        await config_repo.save(existing_config)
        use_case = UpsertUserAgentConfiguration(user_repo, config_repo)

        # When
        result = await use_case.execute(user_id=user.id, llm_backend="anthropic")

        # Then
        assert result.llm_backend == "anthropic"
        saved = await config_repo.find_by_owner(user.id, AgentConfigurationType.USER)
        assert saved is not None
        assert saved.id == existing_config.id
        assert saved.llm_backend == "anthropic"

    async def test_saves_with_user_type(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        config_repo = InMemoryAgentConfigurationRepository()
        use_case = UpsertUserAgentConfiguration(user_repo, config_repo)

        # When
        result = await use_case.execute(user_id=user.id)

        # Then
        assert result.owner_type == AgentConfigurationType.USER
        saved = await config_repo.find_by_owner(user.id, AgentConfigurationType.USER)
        assert saved is not None
        assert saved.owner_type == AgentConfigurationType.USER
