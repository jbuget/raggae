from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.user.get_user_project_defaults import GetUserProjectDefaults
from raggae.application.use_cases.user.upsert_user_project_defaults import UpsertUserProjectDefaults
from raggae.domain.entities.user import User
from raggae.domain.entities.user_project_defaults import UserProjectDefaults
from raggae.domain.exceptions.user_exceptions import UserNotFoundError
from raggae.domain.value_objects.locale import Locale
from raggae.infrastructure.database.repositories.in_memory_user_project_defaults_repository import (
    InMemoryUserProjectDefaultsRepository,
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
        defaults_repo = InMemoryUserProjectDefaultsRepository()
        use_case = GetUserProjectDefaults(
            user_repository=user_repo,
            user_project_defaults_repository=defaults_repo,
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
        defaults_repo = InMemoryUserProjectDefaultsRepository()
        defaults = UserProjectDefaults(user_id=user.id, embedding_backend="openai", llm_backend="anthropic")
        await defaults_repo.save(defaults)
        use_case = GetUserProjectDefaults(
            user_repository=user_repo,
            user_project_defaults_repository=defaults_repo,
        )

        # When
        result = await use_case.execute(user_id=user.id)

        # Then
        assert result is not None
        assert result.user_id == user.id
        assert result.embedding_backend == "openai"
        assert result.llm_backend == "anthropic"

    @pytest.mark.asyncio
    async def test_raises_when_user_not_found(self) -> None:
        # Given
        user_repo = InMemoryUserRepository()
        defaults_repo = InMemoryUserProjectDefaultsRepository()
        use_case = GetUserProjectDefaults(
            user_repository=user_repo,
            user_project_defaults_repository=defaults_repo,
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
        defaults_repo = InMemoryUserProjectDefaultsRepository()
        use_case = UpsertUserProjectDefaults(
            user_repository=user_repo,
            user_project_defaults_repository=defaults_repo,
        )

        # When
        result = await use_case.execute(
            user_id=user.id,
            embedding_backend="openai",
            llm_backend="anthropic",
            retrieval_top_k=5,
        )

        # Then
        assert result.user_id == user.id
        assert result.embedding_backend == "openai"
        assert result.llm_backend == "anthropic"
        assert result.retrieval_top_k == 5

    @pytest.mark.asyncio
    async def test_replaces_existing_defaults(self) -> None:
        # Given
        user = _make_user()
        user_repo = InMemoryUserRepository()
        await user_repo.save(user)
        defaults_repo = InMemoryUserProjectDefaultsRepository()
        await defaults_repo.save(
            UserProjectDefaults(user_id=user.id, embedding_backend="openai", llm_backend="openai")
        )
        use_case = UpsertUserProjectDefaults(
            user_repository=user_repo,
            user_project_defaults_repository=defaults_repo,
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
        defaults_repo = InMemoryUserProjectDefaultsRepository()
        use_case = UpsertUserProjectDefaults(
            user_repository=user_repo,
            user_project_defaults_repository=defaults_repo,
        )

        # When / Then
        with pytest.raises(UserNotFoundError):
            await use_case.execute(user_id=uuid4(), llm_backend="openai")
