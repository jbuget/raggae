from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.dto.document_structure_analysis_dto import DocumentStructureAnalysisDTO
from raggae.application.services.document_indexing_service import DocumentIndexingService
from raggae.domain.entities.document import Document
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestDocumentIndexingService:
    @pytest.fixture
    def mock_document_chunk_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_document_text_extractor(self) -> AsyncMock:
        extractor = AsyncMock()
        extractor.extract_text.return_value = "hello\x00 world\r\n\r\nfrom raggae   "
        return extractor

    @pytest.fixture
    def mock_text_sanitizer_service(self) -> AsyncMock:
        sanitizer = AsyncMock()
        sanitizer.sanitize_text.return_value = "hello world\n\nfrom raggae"
        return sanitizer

    @pytest.fixture
    def mock_document_structure_analyzer(self) -> AsyncMock:
        analyzer = AsyncMock()
        analyzer.analyze_text.return_value = DocumentStructureAnalysisDTO(
            has_headings=False,
            paragraph_count=3,
            average_paragraph_length=120,
        )
        return analyzer

    @pytest.fixture
    def mock_text_chunker_service(self) -> AsyncMock:
        chunker = AsyncMock()
        chunker.chunk_text.return_value = ["hello world", "from raggae"]
        return chunker

    @pytest.fixture
    def mock_embedding_service(self) -> AsyncMock:
        embedding = AsyncMock()
        embedding.embed_texts.return_value = [[0.1, 0.2], [0.3, 0.4]]
        return embedding

    @pytest.fixture
    def document(self) -> Document:
        return Document(
            id=uuid4(),
            project_id=uuid4(),
            file_name="doc.txt",
            content_type="text/plain",
            file_size=23,
            storage_key="projects/p1/documents/d1-doc.txt",
            created_at=datetime.now(UTC),
        )

    async def test_run_pipeline_extracts_chunks_and_embeds(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
    ) -> None:
        # Given
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        result = await service.run_pipeline(document, b"hello world from raggae")

        # Then
        mock_document_text_extractor.extract_text.assert_called_once()
        mock_text_sanitizer_service.sanitize_text.assert_called_once_with(
            "hello\x00 world\r\n\r\nfrom raggae   "
        )
        mock_document_structure_analyzer.analyze_text.assert_called_once_with(
            "hello world\n\nfrom raggae"
        )
        mock_text_chunker_service.chunk_text.assert_called_once_with(
            "hello world\n\nfrom raggae",
            strategy=ChunkingStrategy.PARAGRAPH,
        )
        mock_embedding_service.embed_texts.assert_called_once_with(["hello world", "from raggae"])
        mock_document_chunk_repository.delete_by_document_id.assert_called_once_with(document.id)
        mock_document_chunk_repository.save_many.assert_called_once()
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        assert len(saved_chunks) == 2
        assert saved_chunks[0].content == "hello world"
        assert saved_chunks[1].content == "from raggae"
        assert result.processing_strategy == ChunkingStrategy.PARAGRAPH

    async def test_run_pipeline_with_llamaindex_backend(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
    ) -> None:
        # Given
        mock_text_chunker_service.last_splitter_name = "sentence"
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
            chunker_backend="llamaindex",
        )

        # When
        result = await service.run_pipeline(document, b"hello world from raggae")

        # Then
        mock_document_structure_analyzer.analyze_text.assert_not_called()
        mock_text_chunker_service.chunk_text.assert_called_once_with(
            "hello world\n\nfrom raggae",
            strategy=ChunkingStrategy.FIXED_WINDOW,
        )
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        assert saved_chunks[0].metadata_json["chunker_backend"] == "llamaindex"
        assert saved_chunks[0].metadata_json["llamaindex_splitter"] == "sentence"
        assert result.processing_strategy == ChunkingStrategy.FIXED_WINDOW

    async def test_run_pipeline_with_empty_chunks(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
    ) -> None:
        # Given
        mock_text_chunker_service.chunk_text.return_value = []
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        result = await service.run_pipeline(document, b"empty doc")

        # Then
        mock_embedding_service.embed_texts.assert_not_called()
        mock_document_chunk_repository.save_many.assert_not_called()
        mock_document_chunk_repository.delete_by_document_id.assert_called_once_with(document.id)
        assert result.processing_strategy is not None

    async def test_run_pipeline_metadata_fields(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
    ) -> None:
        # Given
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        await service.run_pipeline(document, b"hello world from raggae")

        # Then
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        metadata = saved_chunks[0].metadata_json
        assert metadata["metadata_version"] == 1
        assert metadata["processing_strategy"] == "paragraph"
        assert metadata["source_type"] == "paragraph"
        assert metadata["chunker_backend"] == "native"
        assert metadata["llamaindex_splitter"] is None
