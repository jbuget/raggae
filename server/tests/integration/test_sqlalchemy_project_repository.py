from datetime import UTC, datetime
from uuid import uuid4

import pytest
from raggae.domain.entities.project import Project
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


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
    async def test_integration_persists_project_ingestion_settings(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repository = SQLAlchemyProjectRepository(session_factory=session_factory)
        project = Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Project",
            description="desc",
            system_prompt="prompt",
            is_published=False,
            created_at=datetime.now(UTC),
            chunking_strategy=ChunkingStrategy.SEMANTIC,
            parent_child_chunking=True,
            reindex_status="in_progress",
            reindex_progress=3,
            reindex_total=10,
            embedding_backend="openai",
            embedding_model="text-embedding-3-small",
            embedding_api_key_encrypted="enc-embedding",
            llm_backend="gemini",
            llm_model="gemini-2.0-flash",
            llm_api_key_encrypted="enc-llm",
            retrieval_strategy="fulltext",
            retrieval_top_k=11,
            retrieval_min_score=0.37,
            chat_history_window_size=10,
            chat_history_max_chars=5000,
        )

        # When
        await repository.save(project)
        found = await repository.find_by_id(project.id)

        # Then
        assert found is not None
        assert found.chunking_strategy == ChunkingStrategy.SEMANTIC
        assert found.parent_child_chunking is True
        assert found.reindex_status == "in_progress"
        assert found.reindex_progress == 3
        assert found.reindex_total == 10
        assert found.embedding_backend == "openai"
        assert found.embedding_model == "text-embedding-3-small"
        assert found.embedding_api_key_encrypted == "enc-embedding"
        assert found.llm_backend == "gemini"
        assert found.llm_model == "gemini-2.0-flash"
        assert found.llm_api_key_encrypted == "enc-llm"
        assert found.retrieval_strategy == "fulltext"
        assert found.retrieval_top_k == 11
        assert found.retrieval_min_score == 0.37
        assert found.chat_history_window_size == 10
        assert found.chat_history_max_chars == 5000
