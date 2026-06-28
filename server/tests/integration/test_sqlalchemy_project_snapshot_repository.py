from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_project_snapshot_repository import (
    SQLAlchemyProjectSnapshotRepository,
)


class TestSQLAlchemyProjectSnapshotRepository:
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

    def _make_snapshot(self, **kwargs) -> ProjectSnapshot:
        defaults = {
            "id": uuid4(),
            "project_id": uuid4(),
            "version_number": 1,
            "label": None,
            "created_at": datetime.now(UTC),
            "created_by_user_id": uuid4(),
            "name": "Test Project",
            "description": "A project",
            "system_prompt": "You are helpful.",
            "is_published": False,
            "organization_id": None,
            "restored_from_version": None,
        }
        return ProjectSnapshot(**{**defaults, **kwargs})

    @pytest.mark.integration
    async def test_integration_save_and_find_by_version(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        # Given
        repo = SQLAlchemyProjectSnapshotRepository(session_factory=session_factory)
        snapshot = self._make_snapshot(retrieval_top_k=10, retrieval_min_score=0.5)

        # When
        await repo.save(snapshot)
        result = await repo.find_by_project_and_version(snapshot.project_id, 1)

        # Then
        assert result is not None
        assert result.retrieval_top_k == 10
        assert result.retrieval_min_score == 0.5

    @pytest.mark.integration
    async def test_integration_save_preserves_zero_numeric_values(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        """Régression : les champs numériques à 0 ne doivent pas être remplacés par la valeur par défaut.

        Le pattern `snapshot.field or DEFAULT` écrase 0 (falsy) par le défaut.
        Le pattern correct est `field if field is not None else DEFAULT`.
        """
        # Given
        repo = SQLAlchemyProjectSnapshotRepository(session_factory=session_factory)
        snapshot = self._make_snapshot(
            retrieval_top_k=0,
            reranker_candidate_multiplier=0,
            chat_history_window_size=0,
            chat_history_max_chars=0,
        )

        # When
        await repo.save(snapshot)
        result = await repo.find_by_project_and_version(snapshot.project_id, 1)

        # Then
        assert result is not None
        assert result.retrieval_top_k == 0, "retrieval_top_k=0 ne doit pas être remplacé par 8"
        assert result.reranker_candidate_multiplier == 0, (
            "reranker_candidate_multiplier=0 ne doit pas être remplacé par 3"
        )
        assert result.chat_history_window_size == 0, (
            "chat_history_window_size=0 ne doit pas être remplacé par 8"
        )
        assert result.chat_history_max_chars == 0, (
            "chat_history_max_chars=0 ne doit pas être remplacé par 4000"
        )
