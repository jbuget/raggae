from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.document.upload_document import (
    UploadDocument,
    UploadDocumentItem,
)
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestUploadDocuments:
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
    def use_case(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
    ) -> UploadDocument:
        return UploadDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            max_file_size=104857600,
        )

    async def test_upload_documents_partial_success_with_duplicate_in_request(
        self,
        use_case: UploadDocument,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Test",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        files = [
            UploadDocumentItem(
                file_name="doc.txt",
                file_content=b"content-1",
                content_type="text/plain",
            ),
            UploadDocumentItem(
                file_name="doc.txt",
                file_content=b"content-2",
                content_type="text/plain",
            ),
        ]

        # When
        result = await use_case.execute_many(
            project_id=project_id,
            user_id=user_id,
            files=files,
        )

        # Then
        assert result.total == 2
        assert result.succeeded == 1
        assert result.failed == 1
        assert len(result.created) == 1
        assert len(result.errors) == 1
        assert result.errors[0].code == "DUPLICATE_IN_REQUEST"
        assert result.errors[0].filename == "doc.txt"

    async def test_upload_documents_renames_file_name_when_already_exists_in_project(
        self,
        use_case: UploadDocument,
        mock_project_repository: AsyncMock,
        mock_document_repository: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Test",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_document_repository.find_by_project_id.return_value = [
            Document(
                id=uuid4(),
                project_id=project_id,
                file_name="guide.md",
                content_type="text/markdown",
                file_size=123,
                storage_key="projects/p/documents/d-guide.md",
                created_at=datetime.now(UTC),
                processing_strategy=None,
            )
        ]

        # When
        result = await use_case.execute_many(
            project_id=project_id,
            user_id=user_id,
            files=[
                UploadDocumentItem(
                    file_name="guide.md",
                    file_content=b"# Guide",
                    content_type="text/markdown",
                )
            ],
        )

        # Then
        assert result.succeeded == 1
        assert result.created[0].stored_filename == "guide-copie-1.md"

    async def test_upload_documents_skips_when_same_name_already_indexed(
        self,
        use_case: UploadDocument,
        mock_project_repository: AsyncMock,
        mock_document_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Test",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_document_repository.find_by_project_id.return_value = [
            Document(
                id=uuid4(),
                project_id=project_id,
                file_name="guide.md",
                content_type="text/markdown",
                file_size=123,
                storage_key="projects/p/documents/d-guide.md",
                created_at=datetime.now(UTC),
                processing_strategy=ChunkingStrategy.FIXED_WINDOW,
            )
        ]

        # When
        result = await use_case.execute_many(
            project_id=project_id,
            user_id=user_id,
            files=[
                UploadDocumentItem(
                    file_name="guide.md",
                    file_content=b"# Guide",
                    content_type="text/markdown",
                )
            ],
        )

        # Then
        assert result.total == 1
        assert result.succeeded == 0
        assert result.failed == 1
        assert result.errors[0].code == "ALREADY_INDEXED"
        assert result.errors[0].filename == "guide.md"
        mock_file_storage_service.upload_file.assert_not_called()

    async def test_upload_documents_processing_failure_cleans_up_and_continues(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Test",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_document_repository.find_by_project_id.return_value = []
        from raggae.application.services.document_indexing_service import (
            DocumentIndexingService,
        )

        extractor = AsyncMock()
        extractor.extract_text.return_value = "hello"
        sanitizer = AsyncMock()
        sanitizer.sanitize_text.return_value = "hello"
        analyzer = AsyncMock()
        analyzer.analyze_text.return_value = AsyncMock(
            has_headings=False,
            paragraph_count=1,
            average_paragraph_length=50,
        )
        chunker = AsyncMock()
        chunker.chunk_text.return_value = ["hello"]
        embedding = AsyncMock()
        embedding.embed_texts.side_effect = EmbeddingGenerationError("boom")
        chunk_repo = AsyncMock()
        indexing_service = DocumentIndexingService(
            document_chunk_repository=chunk_repo,
            document_text_extractor=extractor,
            text_sanitizer_service=sanitizer,
            document_structure_analyzer=analyzer,
            text_chunker_service=chunker,
            embedding_service=embedding,
        )
        use_case = UploadDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            max_file_size=104857600,
            processing_mode="sync",
            document_chunk_repository=chunk_repo,
            document_indexing_service=indexing_service,
        )

        # When
        result = await use_case.execute_many(
            project_id=project_id,
            user_id=user_id,
            files=[
                UploadDocumentItem(
                    file_name="a.txt",
                    file_content=b"a",
                    content_type="text/plain",
                ),
                UploadDocumentItem(
                    file_name="b.txt",
                    file_content=b"b",
                    content_type="text/plain",
                ),
            ],
        )

        # Then
        assert result.total == 2
        assert result.succeeded == 0
        assert result.failed == 2
        assert [error.code for error in result.errors] == [
            "PROCESSING_FAILED",
            "PROCESSING_FAILED",
        ]
        assert mock_file_storage_service.delete_file.await_count == 2
        assert mock_document_repository.delete.await_count == 2
