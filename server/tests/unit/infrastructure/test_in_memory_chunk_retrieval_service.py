from datetime import UTC, datetime
from uuid import uuid4

from raggae.domain.entities.document import Document
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.infrastructure.database.repositories.in_memory_document_chunk_repository import (
    InMemoryDocumentChunkRepository,
)
from raggae.infrastructure.database.repositories.in_memory_document_repository import (
    InMemoryDocumentRepository,
)
from raggae.infrastructure.services.in_memory_chunk_retrieval_service import (
    InMemoryChunkRetrievalService,
)


class TestInMemoryChunkRetrievalService:
    async def test_retrieve_chunks_returns_top_k_sorted_by_score(self) -> None:
        # Given
        project_id = uuid4()
        document_repository = InMemoryDocumentRepository()
        chunk_repository = InMemoryDocumentChunkRepository()
        service = InMemoryChunkRetrievalService(
            document_repository=document_repository,
            document_chunk_repository=chunk_repository,
        )

        doc_a = Document(
            id=uuid4(),
            project_id=project_id,
            file_name="a.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="a",
            created_at=datetime.now(UTC),
        )
        doc_b = Document(
            id=uuid4(),
            project_id=project_id,
            file_name="b.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="b",
            created_at=datetime.now(UTC),
        )
        await document_repository.save(doc_a)
        await document_repository.save(doc_b)

        await chunk_repository.save_many(
            [
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc_a.id,
                    chunk_index=0,
                    content="first",
                    embedding=[1.0, 0.0],
                    created_at=datetime.now(UTC),
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc_b.id,
                    chunk_index=0,
                    content="second",
                    embedding=[0.8, 0.2],
                    created_at=datetime.now(UTC),
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc_b.id,
                    chunk_index=1,
                    content="third",
                    embedding=[0.0, 1.0],
                    created_at=datetime.now(UTC),
                ),
            ]
        )

        # When
        result = await service.retrieve_chunks(
            project_id=project_id,
            query_embedding=[1.0, 0.0],
            limit=2,
        )

        # Then
        assert len(result) == 2
        assert result[0].content == "first"
        assert result[1].content == "second"
        assert result[0].score > result[1].score

    async def test_retrieve_chunks_returns_empty_list_when_project_has_no_chunks(self) -> None:
        # Given
        project_id = uuid4()
        document_repository = InMemoryDocumentRepository()
        chunk_repository = InMemoryDocumentChunkRepository()
        service = InMemoryChunkRetrievalService(
            document_repository=document_repository,
            document_chunk_repository=chunk_repository,
        )

        # When
        result = await service.retrieve_chunks(
            project_id=project_id,
            query_embedding=[1.0, 0.0],
            limit=5,
        )

        # Then
        assert result == []

    async def test_retrieve_chunks_filters_by_min_score(self) -> None:
        # Given
        project_id = uuid4()
        document_repository = InMemoryDocumentRepository()
        chunk_repository = InMemoryDocumentChunkRepository()
        service = InMemoryChunkRetrievalService(
            document_repository=document_repository,
            document_chunk_repository=chunk_repository,
        )
        doc = Document(
            id=uuid4(),
            project_id=project_id,
            file_name="a.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="a",
            created_at=datetime.now(UTC),
        )
        await document_repository.save(doc)
        await chunk_repository.save_many(
            [
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc.id,
                    chunk_index=0,
                    content="first",
                    embedding=[1.0, 0.0],
                    created_at=datetime.now(UTC),
                ),
                DocumentChunk(
                    id=uuid4(),
                    document_id=doc.id,
                    chunk_index=1,
                    content="second",
                    embedding=[0.2, 0.8],
                    created_at=datetime.now(UTC),
                ),
            ]
        )

        # When
        result = await service.retrieve_chunks(
            project_id=project_id,
            query_embedding=[1.0, 0.0],
            limit=5,
            min_score=0.9,
        )

        # Then
        assert len(result) == 1
        assert result[0].content == "first"
