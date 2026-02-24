from datetime import UTC, datetime
from uuid import uuid4

import pytest
from raggae.domain.entities.document import Document
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_document_repository import (
    SQLAlchemyDocumentRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class TestSQLAlchemyDocumentRepository:
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
    async def test_integration_save_find_and_delete_document(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        repository = SQLAlchemyDocumentRepository(session_factory=session_factory)
        document = Document(
            id=uuid4(),
            project_id=uuid4(),
            file_name="test.pdf",
            content_type="application/pdf",
            file_size=42,
            storage_key="documents/test.pdf",
            created_at=datetime.now(UTC),
        )

        await repository.save(document)
        found = await repository.find_by_id(document.id)
        assert found is not None
        assert found.file_name == "test.pdf"
        assert found.processing_strategy is None

        found_by_project = await repository.find_by_project_id(document.project_id)
        assert len(found_by_project) == 1
        assert found_by_project[0].processing_strategy is None

        await repository.delete(document.id)
        deleted = await repository.find_by_id(document.id)
        assert deleted is None

    @pytest.mark.integration
    async def test_integration_save_document_with_processing_strategy(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        repository = SQLAlchemyDocumentRepository(session_factory=session_factory)
        document = Document(
            id=uuid4(),
            project_id=uuid4(),
            file_name="test.md",
            content_type="text/markdown",
            file_size=128,
            storage_key="documents/test.md",
            created_at=datetime.now(UTC),
            processing_strategy=ChunkingStrategy.HEADING_SECTION,
        )

        await repository.save(document)
        found = await repository.find_by_id(document.id)

        assert found is not None
        assert found.processing_strategy == ChunkingStrategy.HEADING_SECTION

        await repository.delete(document.id)
        deleted = await repository.find_by_id(document.id)
        assert deleted is None
