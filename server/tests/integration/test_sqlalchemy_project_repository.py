from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from raggae.domain.entities.project import Project
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)


class TestSQLAlchemyProjectRepository:
    @pytest.fixture
    async def session_factory(self) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            "postgresql+asyncpg://test:test@localhost:5433/raggae_test",
            echo=False,
        )
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        except Exception as exc:  # pragma: no cover - environment dependent
            pytest.skip(f"PostgreSQL test database is not reachable: {exc}")

        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        yield factory

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    @pytest.mark.integration
    async def test_integration_save_and_find_by_id(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repository = SQLAlchemyProjectRepository(session_factory=session_factory)
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Test Project",
            description="desc",
            system_prompt="prompt",
            is_published=True,
            created_at=datetime.now(UTC),
            reindex_status="in_progress",
            reindex_progress=3,
            reindex_total=10,
        )

        # When
        await repository.save(project)
        found = await repository.find_by_id(project.id)

        # Then
        assert found is not None
        assert found.id == project.id
        assert found.name == "Test Project"
        assert found.description == "desc"
        assert found.system_prompt == "prompt"
        assert found.is_published is True
        assert found.reindex_status == "in_progress"
        assert found.reindex_progress == 3
        assert found.reindex_total == 10

    @pytest.mark.integration
    async def test_integration_update_project(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repository = SQLAlchemyProjectRepository(session_factory=session_factory)
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Original",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        await repository.save(project)

        # When
        from dataclasses import replace
        updated = replace(project, name="Updated", is_published=True)
        await repository.save(updated)
        found = await repository.find_by_id(project.id)

        # Then
        assert found is not None
        assert found.name == "Updated"
        assert found.is_published is True

    @pytest.mark.integration
    async def test_integration_find_by_id_returns_none_when_missing(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        repository = SQLAlchemyProjectRepository(session_factory=session_factory)
        assert await repository.find_by_id(uuid4()) is None

    @pytest.mark.integration
    async def test_integration_delete_removes_project(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repository = SQLAlchemyProjectRepository(session_factory=session_factory)
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="To Delete",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        await repository.save(project)

        # When
        await repository.delete(project.id)

        # Then
        assert await repository.find_by_id(project.id) is None
