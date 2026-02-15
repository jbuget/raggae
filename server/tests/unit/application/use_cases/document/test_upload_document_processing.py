from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.dto.document_structure_analysis_dto import DocumentStructureAnalysisDTO
from raggae.application.use_cases.document.upload_document import UploadDocument
from raggae.domain.entities.project import Project
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestUploadDocumentProcessing:
    @pytest.fixture
    def mock_document_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_file_storage_service(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_document_chunk_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_document_text_extractor(self) -> AsyncMock:
        extractor = AsyncMock()
        extractor.extract_text.return_value = "hello\x00 world\r\n\r\nfrom raggae   "
        return extractor

    @pytest.fixture
    def mock_text_chunker_service(self) -> AsyncMock:
        chunker = AsyncMock()
        chunker.chunk_text.return_value = ["hello world", "from raggae"]
        return chunker

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
    def mock_text_sanitizer_service(self) -> AsyncMock:
        sanitizer = AsyncMock()
        sanitizer.sanitize_text.return_value = "hello world\n\nfrom raggae"
        return sanitizer

    @pytest.fixture
    def mock_embedding_service(self) -> AsyncMock:
        embedding = AsyncMock()
        embedding.embed_texts.return_value = [[0.1, 0.2], [0.3, 0.4]]
        return embedding

    async def test_upload_document_sync_processing_saves_chunks(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_text_chunker_service.last_splitter_name = "sentence"
        use_case = UploadDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="doc.txt",
            file_content=b"hello world from raggae",
            content_type="text/plain",
        )

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
        mock_document_chunk_repository.save_many.assert_called_once()
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        assert saved_chunks[0].metadata_json is not None
        assert saved_chunks[0].metadata_json["metadata_version"] == 1
        assert saved_chunks[0].metadata_json["processing_strategy"] == "paragraph"
        assert saved_chunks[0].metadata_json["source_type"] == "paragraph"
        assert saved_chunks[0].metadata_json["chunker_backend"] == "native"
        assert mock_document_repository.save.call_count == 2
        second_saved_document = mock_document_repository.save.call_args_list[1].args[0]
        assert second_saved_document.processing_strategy == ChunkingStrategy.PARAGRAPH

    async def test_upload_document_processing_off_does_not_save_chunks(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_text_chunker_service.last_splitter_name = "sentence"
        use_case = UploadDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            max_file_size=104857600,
            processing_mode="off",
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="doc.txt",
            file_content=b"hello world from raggae",
            content_type="text/plain",
        )

        # Then
        mock_document_chunk_repository.save_many.assert_not_called()
        mock_document_text_extractor.extract_text.assert_not_called()
        mock_text_sanitizer_service.sanitize_text.assert_not_called()
        mock_document_structure_analyzer.analyze_text.assert_not_called()
        mock_text_chunker_service.chunk_text.assert_not_called()
        mock_embedding_service.embed_texts.assert_not_called()

    async def test_upload_document_sync_processing_selects_heading_strategy(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_document_structure_analyzer.analyze_text.return_value = DocumentStructureAnalysisDTO(
            has_headings=True,
            paragraph_count=1,
            average_paragraph_length=20,
        )
        use_case = UploadDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="doc.md",
            file_content=b"# Title\n\nBody",
            content_type="text/markdown",
        )

        # Then
        mock_text_chunker_service.chunk_text.assert_called_once_with(
            "hello world\n\nfrom raggae",
            strategy=ChunkingStrategy.HEADING_SECTION,
        )

    async def test_upload_document_processing_async_does_not_save_chunks(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_text_chunker_service.last_splitter_name = "sentence"
        use_case = UploadDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            max_file_size=104857600,
            processing_mode="async",
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="doc.txt",
            file_content=b"hello world from raggae",
            content_type="text/plain",
        )

        # Then
        mock_document_chunk_repository.save_many.assert_not_called()
        mock_document_text_extractor.extract_text.assert_not_called()
        mock_text_sanitizer_service.sanitize_text.assert_not_called()
        mock_document_structure_analyzer.analyze_text.assert_not_called()
        mock_text_chunker_service.chunk_text.assert_not_called()
        mock_embedding_service.embed_texts.assert_not_called()

    async def test_upload_document_sync_processing_llamaindex_ignores_strategy_selector(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_text_chunker_service.last_splitter_name = "sentence"
        use_case = UploadDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=mock_document_chunk_repository,
            document_text_extractor=mock_document_text_extractor,
            text_sanitizer_service=mock_text_sanitizer_service,
            document_structure_analyzer=mock_document_structure_analyzer,
            text_chunker_service=mock_text_chunker_service,
            embedding_service=mock_embedding_service,
            chunker_backend="llamaindex",
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="doc.txt",
            file_content=b"hello world from raggae",
            content_type="text/plain",
        )

        # Then
        mock_document_structure_analyzer.analyze_text.assert_not_called()
        mock_text_chunker_service.chunk_text.assert_called_once_with(
            "hello world\n\nfrom raggae",
            strategy=ChunkingStrategy.FIXED_WINDOW,
        )
        saved_chunks = mock_document_chunk_repository.save_many.call_args.args[0]
        assert saved_chunks[0].metadata_json is not None
        assert saved_chunks[0].metadata_json["processing_strategy"] == "fixed_window"
        assert saved_chunks[0].metadata_json["source_type"] == "fixed_window"
        assert saved_chunks[0].metadata_json["chunker_backend"] == "llamaindex"
        assert saved_chunks[0].metadata_json["llamaindex_splitter"] == "sentence"

    async def test_upload_document_invalid_processing_mode_raises_value_error(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_chunk_repository: AsyncMock,
        mock_document_text_extractor: AsyncMock,
        mock_text_sanitizer_service: AsyncMock,
        mock_document_structure_analyzer: AsyncMock,
        mock_text_chunker_service: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # When / Then
        with pytest.raises(ValueError):
            UploadDocument(
                document_repository=mock_document_repository,
                project_repository=mock_project_repository,
                file_storage_service=mock_file_storage_service,
                max_file_size=104857600,
                processing_mode="invalid",
                document_chunk_repository=mock_document_chunk_repository,
                document_text_extractor=mock_document_text_extractor,
                text_sanitizer_service=mock_text_sanitizer_service,
                document_structure_analyzer=mock_document_structure_analyzer,
                text_chunker_service=mock_text_chunker_service,
                embedding_service=mock_embedding_service,
            )
