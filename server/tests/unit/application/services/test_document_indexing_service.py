from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.dto.document_structure_analysis_dto import DocumentStructureAnalysisDTO
from raggae.application.interfaces.services.file_metadata_extractor import FileMetadata
from raggae.application.services.document_indexing_service import DocumentIndexingService
from raggae.application.services.parent_child_chunking_service import (
    ParentChildChunkingService,
)
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.value_objects.chunk_level import ChunkLevel
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
    def mock_language_detector(self) -> AsyncMock:
        detector = AsyncMock()
        detector.detect_language.return_value = "fr"
        return detector

    @pytest.fixture
    def mock_keyword_extractor(self) -> AsyncMock:
        extractor = AsyncMock()
        extractor.extract_keywords.return_value = ["workflow", "borne"]
        return extractor

    @pytest.fixture
    def mock_file_metadata_extractor(self) -> AsyncMock:
        extractor = AsyncMock()
        extractor.extract_metadata.return_value = FileMetadata(
            title="Titre PDF",
            authors=["Alice", "Bob"],
            document_date=datetime(2026, 1, 27, tzinfo=UTC).date(),
        )
        return extractor

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

    @pytest.fixture
    def project(self) -> Project:
        return Project(
            id=uuid4(),
            user_id=uuid4(),
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
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
        project: Project,
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
        result = await service.run_pipeline(document, project, b"hello world from raggae")

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
            embedding_service=mock_embedding_service,
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
        project: Project,
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
        result = await service.run_pipeline(document, project, b"hello world from raggae")

        # Then
        mock_document_structure_analyzer.analyze_text.assert_called_once_with(
            "hello world\n\nfrom raggae"
        )
        mock_text_chunker_service.chunk_text.assert_called_once_with(
            "hello world\n\nfrom raggae",
            strategy=ChunkingStrategy.PARAGRAPH,
            embedding_service=mock_embedding_service,
        )
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        assert saved_chunks[0].metadata_json["chunker_backend"] == "llamaindex"
        assert saved_chunks[0].metadata_json["llamaindex_splitter"] == "sentence"
        assert result.processing_strategy == ChunkingStrategy.PARAGRAPH

    async def test_run_pipeline_with_empty_chunks(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
        project: Project,
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
        result = await service.run_pipeline(document, project, b"empty doc")

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
        project: Project,
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
        await service.run_pipeline(document, project, b"hello world from raggae")

        # Then
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        metadata = saved_chunks[0].metadata_json
        assert metadata["metadata_version"] == 1
        assert metadata["processing_strategy"] == "paragraph"
        assert metadata["source_type"] == "paragraph"
        assert metadata["chunker_backend"] == "native"
        assert metadata["llamaindex_splitter"] is None

    async def test_run_pipeline_adds_pdf_page_metadata_to_chunks(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
        project: Project,
    ) -> None:
        # Given
        pdf_document = Document(
            id=document.id,
            project_id=document.project_id,
            file_name="report.pdf",
            content_type="application/pdf",
            file_size=document.file_size,
            storage_key=document.storage_key,
            created_at=document.created_at,
        )
        mock_document_text_extractor.extract_text.return_value = (
            "[[PAGE:1]]\nDécision A\n\n[[PAGE:2]]\nDécision B"
        )
        mock_text_sanitizer_service.sanitize_text.return_value = (
            "[[PAGE:1]]\nDécision A\n\n[[PAGE:2]]\nDécision B"
        )
        mock_text_chunker_service.chunk_text.return_value = [
            "[[PAGE:1]]\nDécision A",
            "[[PAGE:1]]\nSuite [[PAGE:2]]\nDécision B",
        ]

        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        await service.run_pipeline(pdf_document, project, b"%PDF-1.7")

        # Then
        mock_embedding_service.embed_texts.assert_called_once_with(
            ["Décision A", "Suite \nDécision B"]
        )
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        assert saved_chunks[0].content == "Décision A"
        assert saved_chunks[0].metadata_json["pages"] == [1]
        assert saved_chunks[0].metadata_json["page_start"] == 1
        assert saved_chunks[0].metadata_json["page_end"] == 1
        assert saved_chunks[1].metadata_json["pages"] == [1, 2]
        assert saved_chunks[1].metadata_json["page_start"] == 1
        assert saved_chunks[1].metadata_json["page_end"] == 2

    async def test_run_pipeline_enriches_document_metadata(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        mock_language_detector: AsyncMock,
        mock_keyword_extractor: AsyncMock,
        mock_file_metadata_extractor: AsyncMock,
        document: Document,
        project: Project,
    ) -> None:
        # Given
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
            language_detector=mock_language_detector,
            keyword_extractor=mock_keyword_extractor,
            file_metadata_extractor=mock_file_metadata_extractor,
        )

        # When
        result = await service.run_pipeline(document, project, b"%PDF-1.7")

        # Then
        assert result.language == "fr"
        assert result.keywords == ["workflow", "borne"]
        assert result.title == "Titre PDF"
        assert result.authors == ["Alice", "Bob"]
        assert result.document_date is not None
        mock_file_metadata_extractor.extract_metadata.assert_called_once()
        mock_language_detector.detect_language.assert_called_once_with(
            "hello\x00 world\r\n\r\nfrom raggae   "
        )
        mock_keyword_extractor.extract_keywords.assert_called_once_with(
            "hello world\n\nfrom raggae"
        )

    async def test_run_pipeline_metadata_extractor_failure_does_not_block_pipeline(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        mock_language_detector: AsyncMock,
        mock_keyword_extractor: AsyncMock,
        mock_file_metadata_extractor: AsyncMock,
        document: Document,
        project: Project,
    ) -> None:
        # Given
        mock_language_detector.detect_language.side_effect = RuntimeError("boom")
        mock_keyword_extractor.extract_keywords.side_effect = RuntimeError("boom")
        mock_file_metadata_extractor.extract_metadata.side_effect = RuntimeError("boom")
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
            language_detector=mock_language_detector,
            keyword_extractor=mock_keyword_extractor,
            file_metadata_extractor=mock_file_metadata_extractor,
        )

        # When
        result = await service.run_pipeline(document, project, b"%PDF-1.7")

        # Then
        assert result.language is None
        assert result.keywords is None
        assert result.title is None
        assert result.authors is None
        assert result.document_date is None
        mock_document_chunk_repository.save_many.assert_called_once()

    async def test_run_pipeline_uses_project_chunking_strategy_when_not_auto(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
        project: Project,
    ) -> None:
        # Given
        project = Project(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            system_prompt=project.system_prompt,
            is_published=project.is_published,
            created_at=project.created_at,
            chunking_strategy=ChunkingStrategy.SEMANTIC,
        )
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        result = await service.run_pipeline(document, project, b"%PDF-1.7")

        # Then
        mock_document_structure_analyzer.analyze_text.assert_not_called()
        mock_text_chunker_service.chunk_text.assert_called_once_with(
            "hello world\n\nfrom raggae",
            strategy=ChunkingStrategy.SEMANTIC,
            embedding_service=mock_embedding_service,
        )
        assert result.processing_strategy == ChunkingStrategy.SEMANTIC

    async def test_run_pipeline_with_parent_child_chunking(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
        project: Project,
    ) -> None:
        # Given — project with parent_child_chunking enabled
        project_pc = Project(
            id=project.id,
            user_id=project.user_id,
            name=project.name,
            description=project.description,
            system_prompt=project.system_prompt,
            is_published=project.is_published,
            created_at=project.created_at,
            parent_child_chunking=True,
        )
        mock_embedding_service.embed_texts.return_value = [[0.1, 0.2], [0.3, 0.4]]
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
            parent_child_chunking_service=ParentChildChunkingService(),
        )

        # When
        await service.run_pipeline(document, project_pc, b"hello world from raggae")

        # Then
        mock_document_chunk_repository.save_many.assert_called_once()
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]

        parent_chunks = [c for c in saved_chunks if c.chunk_level == ChunkLevel.PARENT]
        child_chunks = [c for c in saved_chunks if c.chunk_level == ChunkLevel.CHILD]
        assert len(parent_chunks) >= 1
        assert len(child_chunks) >= 1
        assert parent_chunks[0].embedding == [0.0, 0.0]
        assert child_chunks[0].parent_chunk_id == parent_chunks[0].id
        assert child_chunks[0].embedding != []

    async def test_run_pipeline_without_parent_child_uses_standard(
        self,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
        document: Document,
        project: Project,
    ) -> None:
        # Given — service has parent_child service but project doesn't enable it
        service = DocumentIndexingService(
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
            parent_child_chunking_service=ParentChildChunkingService(),
        )

        # When
        await service.run_pipeline(document, project, b"hello world from raggae")

        # Then — all chunks are STANDARD
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        assert all(c.chunk_level == ChunkLevel.STANDARD for c in saved_chunks)
