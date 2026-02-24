from datetime import UTC, datetime
from uuid import uuid4

import pytest
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_document_chunk_repository import (
    SQLAlchemyDocumentChunkRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class TestSQLAlchemyDocumentChunkRepository:
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
    async def test_integration_save_many_and_delete_by_document_id(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        repository = SQLAlchemyDocumentChunkRepository(session_factory=session_factory)
        document_id = uuid4()
        chunks = [
            DocumentChunk(
                id=uuid4(),
                document_id=document_id,
                chunk_index=0,
                content="chunk 1",
                embedding=[0.1] * 1536,
                created_at=datetime.now(UTC),
                metadata_json={"metadata_version": 1, "source_type": "paragraph"},
            ),
            DocumentChunk(
                id=uuid4(),
                document_id=document_id,
                chunk_index=1,
                content="chunk 2",
                embedding=[0.2] * 1536,
                created_at=datetime.now(UTC),
                metadata_json={"metadata_version": 1, "source_type": "paragraph"},
            ),
        ]

        await repository.save_many(chunks)
        found = await repository.find_by_document_id(document_id)
        assert len(found) == 2
        assert found[0].chunk_index == 0
        assert found[0].content == "chunk 1"
        assert found[0].metadata_json == {"metadata_version": 1, "source_type": "paragraph"}
        assert found[1].chunk_index == 1
        assert found[1].content == "chunk 2"
        assert found[1].metadata_json == {"metadata_version": 1, "source_type": "paragraph"}

        await repository.delete_by_document_id(document_id)
        found_after_delete = await repository.find_by_document_id(document_id)
        assert found_after_delete == []
