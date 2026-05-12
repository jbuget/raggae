from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.user.get_user_project_defaults import GetUserProjectDefaults
from raggae.application.use_cases.user.upsert_user_project_defaults import UpsertUserProjectDefaults
from raggae.domain.entities.project_defaults import ProjectDefaults
from raggae.domain.entities.user import User
from raggae.domain.exceptions.project_exceptions import InvalidProjectChunkingStrategyError
from raggae.domain.exceptions.user_exceptions import UserNotFoundError
from raggae.domain.value_objects.locale import Locale
from raggae.domain.value_objects.project_defaults_owner_type import ProjectDefaultsOwnerType
from raggae.infrastructure.database.repositories.in_memory_project_defaults_repository import (
    InMemoryProjectDefaultsRepository,
)
from raggae.infrastructure.database.repositories.in_memory_user_repository import InMemoryUserRepository


def _make_user(user_id=None):
    return User(
        id=user_id or uuid4(),
        email="user@example.com",
        hashed_password="hash",
        full_name="Test User",
        is_active=True,
        created_at=datetime.now(UTC),
        locale=Locale.EN,
    )


class TestGetUserProjectDefaults:
    @pytest.mark.asyncio
    async def test_returns_none_when_no_defaults_configured(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        defaults_repo = InMemoryProjectDefaultsRepository()
        use_case = GetUserProjectDefaults(
            user_repository=user_repo,
            project_defaults_repository=defaults_repo,
        )

        # When
        result = await use_case.execute(user_id=user.id)

        # Then
        assert result is None

    @pytest.mark.asyncio
    async def test_returns_dto_when_defaults_exist(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        defaults_repo = InMemoryProjectDefaultsRepository()
        defaults = ProjectDefaults(
            owner_id=user.id,
            owner_type=ProjectDefaultsOwnerType.USER,
            embedding_backend="openai",
            llm_backend="anthropic",
        )
        await defaults_repo.save(defaults)
        use_case = GetUserProjectDefaults(
            user_repository=user_repo,
            project_defaults_repository=defaults_repo,
        )

        # When
        result = await use_case.execute(user_id=user.id)

        # Then
        assert result is not None
        assert result.owner_id == user.id
        assert result.owner_type == ProjectDefaultsOwnerType.USER
        assert result.embedding_backend == "openai"
        assert result.llm_backend == "anthropic"

    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(self) -> None:
        # Given
        user_repo = InMemoryUserRepository()
        defaults_repo = InMemoryProjectDefaultsRepository()
        use_case = GetUserProjectDefaults(
            user_repository=user_repo,
            project_defaults_repository=defaults_repo,
        )

        # When / Then
        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id=uuid4())


class TestUpsertUserProjectDefaults:
    @pytest.mark.asyncio
    async def test_creates_defaults_when_none_exist(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        defaults_repo = InMemoryProjectDefaultsRepository()
        use_case = UpsertUserProjectDefaults(
            user_repository=user_repo,
            project_defaults_repository=defaults_repo,
        )

        # When
        result = await use_case.execute(
            user_id=user.id,
            embedding_backend="openai",
            llm_backend="anthropic",
            retrieval_top_k=5,
        )

        # Then
        assert result.owner_id == user.id
        assert result.owner_type == ProjectDefaultsOwnerType.USER
        assert result.embedding_backend == "openai"
        assert result.llm_backend == "anthropic"
        assert result.retrieval_top_k == 5

    @pytest.mark.asyncio
    async def test_replaces_existing_defaults(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        defaults_repo = InMemoryProjectDefaultsRepository()
        await defaults_repo.save(
            ProjectDefaults(
                owner_id=user.id,
                owner_type=ProjectDefaultsOwnerType.USER,
                embedding_backend="openai",
                llm_backend="openai",
            )
        )
        use_case = UpsertUserProjectDefaults(
            user_repository=user_repo,
            project_defaults_repository=defaults_repo,
        )

        # When
        result = await use_case.execute(user_id=user.id, llm_backend="anthropic")

        # Then
        assert result.embedding_backend is None
        assert result.llm_backend == "anthropic"

    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(self) -> None:
        # Given
        user_repo = InMemoryUserRepository()
        defaults_repo = InMemoryProjectDefaultsRepository()
        use_case = UpsertUserProjectDefaults(
            user_repository=user_repo,
            project_defaults_repository=defaults_repo,
        )

        # When / Then
        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id=uuid4(), llm_backend="openai")

    @pytest.mark.asyncio
    async def test_raises_invalid_chunking_strategy_error(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        defaults_repo = InMemoryProjectDefaultsRepository()
        use_case = UpsertUserProjectDefaults(
            user_repository=user_repo,
            project_defaults_repository=defaults_repo,
        )

        # When / Then
        with pytest.raises(InvalidProjectChunkingStrategyError):
            await use_case.execute(user_id=user.id, chunking_strategy="invalid_strategy")
