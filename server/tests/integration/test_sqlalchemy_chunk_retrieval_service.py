from datetime import UTC, datetime
from uuid import uuid4

import pytest
from raggae.domain.entities.document import Document
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_document_chunk_repository import (
    SQLAlchemyDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_document_repository import (
    SQLAlchemyDocumentRepository,
)
from raggae.infrastructure.services.sqlalchemy_chunk_retrieval_service import (
    SQLAlchemyChunkRetrievalService,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class TestSQLAlchemyChunkRetrievalService:
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
    async def test_integration_retrieve_chunks_returns_top_k_for_project(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        project_id = uuid4()
        other_project_id = uuid4()

        document_repository = SQLAlchemyDocumentRepository(session_factory=session_factory)
        chunk_repository = SQLAlchemyDocumentChunkRepository(session_factory=session_factory)
        retrieval_service = SQLAlchemyChunkRetrievalService(session_factory=session_factory)

        first_doc = Document(
            id=uuid4(),
            project_id=project_id,
            file_name="first.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="first",
            created_at=datetime.now(UTC),
        )
        second_doc = Document(
            id=uuid4(),
            project_id=project_id,
            file_name="second.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="second",
            created_at=datetime.now(UTC),
        )
        foreign_doc = Document(
            id=uuid4(),
            project_id=other_project_id,
            file_name="foreign.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="foreign",
            created_at=datetime.now(UTC),
        )
        await document_repository.save(first_doc)
        await document_repository.save(second_doc)
        await document_repository.save(foreign_doc)

        await chunk_repository.save_many(
            [
                DocumentChunk(
                    id=uuid4(),
                    document_id=first_doc.id,
                    chunk_index=0,
                    content="first content",
                    embedding=[1.0] + [0.0] * 1535,
                    created_at=datetime.now(UTC),
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_id=second_doc.id,
                    chunk_index=0,
                    content="second content",
                    embedding=[0.8, 0.2] + [0.0] * 1534,
                    created_at=datetime.now(UTC),
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_id=foreign_doc.id,
                    chunk_index=0,
                    content="foreign content",
                    embedding=[1.0] + [0.0] * 1535,
                    created_at=datetime.now(UTC),
                ),
            ]
        )

        # When
        result = await retrieval_service.retrieve_chunks(
            project_id=project_id,
            query_text="first content",
            query_embedding=[1.0] + [0.0] * 1535,
            limit=2,
        )

        # Then
        assert len(result) == 2
        assert result[0].content == "first content"
        assert result[1].content == "second content"
        assert result[0].score >= result[1].score
        assert result[0].vector_score is not None
        assert result[0].fulltext_score is not None
        assert all(item.document_id in {first_doc.id, second_doc.id} for item in result)

    @pytest.mark.integration
    async def test_integration_retrieve_chunks_applies_min_score(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        project_id = uuid4()
        document_repository = SQLAlchemyDocumentRepository(session_factory=session_factory)
        chunk_repository = SQLAlchemyDocumentChunkRepository(session_factory=session_factory)
        retrieval_service = SQLAlchemyChunkRetrievalService(session_factory=session_factory)

        doc = Document(
            id=uuid4(),
            project_id=project_id,
            file_name="first.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="first",
            created_at=datetime.now(UTC),
        )
        await document_repository.save(doc)
        await chunk_repository.save_many(
            [
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc.id,
                    chunk_index=0,
                    content="first content",
                    embedding=[1.0] + [0.0] * 1535,
                    created_at=datetime.now(UTC),
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc.id,
                    chunk_index=1,
                    content="second content",
                    embedding=[0.2, 0.8] + [0.0] * 1534,
                    created_at=datetime.now(UTC),
                ),
            ]
        )

        # When
        result = await retrieval_service.retrieve_chunks(
            project_id=project_id,
            query_text="first content",
            query_embedding=[1.0] + [0.0] * 1535,
            limit=10,
            min_score=0.8,
        )

        # Then
        assert len(result) == 1
        assert result[0].content == "first content"

    @pytest.mark.integration
    async def test_integration_retrieve_chunks_applies_offset(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        project_id = uuid4()
        document_repository = SQLAlchemyDocumentRepository(session_factory=session_factory)
        chunk_repository = SQLAlchemyDocumentChunkRepository(session_factory=session_factory)
        retrieval_service = SQLAlchemyChunkRetrievalService(session_factory=session_factory)

        doc = Document(
            id=uuid4(),
            project_id=project_id,
            file_name="doc.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="doc",
            created_at=datetime.now(UTC),
        )
        await document_repository.save(doc)
        await chunk_repository.save_many(
            [
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc.id,
                    chunk_index=0,
                    content="first hit",
                    embedding=[1.0] + [0.0] * 1535,
                    created_at=datetime.now(UTC),
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc.id,
                    chunk_index=1,
                    content="second hit",
                    embedding=[0.9, 0.1] + [0.0] * 1534,
                    created_at=datetime.now(UTC),
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc.id,
                    chunk_index=2,
                    content="third hit",
                    embedding=[0.8, 0.2] + [0.0] * 1534,
                    created_at=datetime.now(UTC),
                ),
            ]
        )

        # When
        result = await retrieval_service.retrieve_chunks(
            project_id=project_id,
            query_text="hit",
            query_embedding=[1.0] + [0.0] * 1535,
            limit=1,
            offset=1,
        )

        # Then
        assert len(result) == 1
        assert result[0].content == "second hit"
