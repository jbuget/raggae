from dataclasses import replace
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.document.reindex_document import ReindexDocument
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.document_exceptions import DocumentNotFoundError
from raggae.domain.exceptions.project_exceptions import (
    ProjectNotFoundError,
    ProjectReindexInProgressError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.document_status import DocumentStatus


class TestReindexDocument:
    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def project_id(self):
        return uuid4()

    @pytest.fixture
    def document_id(self):
        return uuid4()

    @pytest.fixture
    def project(self, project_id, user_id):
        return Project(
            id=project_id,
            user_id=user_id,
            name="Test",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )

    @pytest.fixture
    def document(self, document_id, project_id):
        return Document(
            id=document_id,
            project_id=project_id,
            file_name="doc.txt",
            content_type="text/plain",
            file_size=23,
            storage_key=f"projects/{project_id}/documents/{document_id}-doc.txt",
            created_at=datetime.now(UTC),
            status=DocumentStatus.INDEXED,
        )

    @pytest.fixture
    def mock_document_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_file_storage_service(self) -> AsyncMock:
        service = AsyncMock()
        service.download_file.return_value = (b"hello world from raggae", "text/plain")
        return service

    @pytest.fixture
    def mock_document_indexing_service(self) -> AsyncMock:
        service = AsyncMock()
        return service

    async def test_reindex_document_success(
        self,
        user_id,
        project_id,
        document_id,
        project,
        document,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_indexing_service: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = project
        mock_document_repository.find_by_id.return_value = document
        processing_document = replace(
            document,
            status=DocumentStatus.PROCESSING,
            processing_strategy=ChunkingStrategy.PARAGRAPH,
        )
        mock_document_indexing_service.run_pipeline.return_value = processing_document
        use_case = ReindexDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            document_indexing_service=mock_document_indexing_service,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            document_id=document_id,
            user_id=user_id,
        )

        # Then
        mock_file_storage_service.download_file.assert_called_once_with(document.storage_key)
        assert mock_document_repository.save.call_count == 2
        # First save: transition to PROCESSING
        first_saved = mock_document_repository.save.call_args_list[0].args[0]
        assert first_saved.status == DocumentStatus.PROCESSING
        # Second save: transition to INDEXED
        second_saved = mock_document_repository.save.call_args_list[1].args[0]
        assert second_saved.status == DocumentStatus.INDEXED
        assert second_saved.processing_strategy == ChunkingStrategy.PARAGRAPH
        assert result.id == document_id
        assert result.processing_strategy == ChunkingStrategy.PARAGRAPH
        assert result.status == DocumentStatus.INDEXED

    async def test_reindex_document_project_not_found_raises_error(
        self,
        user_id,
        project_id,
        document_id,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_indexing_service: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = None
        use_case = ReindexDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            document_indexing_service=mock_document_indexing_service,
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project_id,
                document_id=document_id,
                user_id=user_id,
            )

    async def test_reindex_document_wrong_owner_raises_error(
        self,
        project_id,
        document_id,
        project,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_indexing_service: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = project
        other_user_id = uuid4()
        use_case = ReindexDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            document_indexing_service=mock_document_indexing_service,
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project_id,
                document_id=document_id,
                user_id=other_user_id,
            )

    async def test_reindex_document_not_found_raises_error(
        self,
        user_id,
        project_id,
        document_id,
        project,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_indexing_service: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = project
        mock_document_repository.find_by_id.return_value = None
        use_case = ReindexDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            document_indexing_service=mock_document_indexing_service,
        )

        # When / Then
        with pytest.raises(DocumentNotFoundError):
            await use_case.execute(
                project_id=project_id,
                document_id=document_id,
                user_id=user_id,
            )

    async def test_reindex_document_wrong_project_raises_error(
        self,
        user_id,
        project_id,
        project,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_indexing_service: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = project
        other_project_doc = Document(
            id=uuid4(),
            project_id=uuid4(),  # different project
            file_name="doc.txt",
            content_type="text/plain",
            file_size=23,
            storage_key="projects/other/documents/d-doc.txt",
            created_at=datetime.now(UTC),
        )
        mock_document_repository.find_by_id.return_value = other_project_doc
        use_case = ReindexDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            document_indexing_service=mock_document_indexing_service,
        )

        # When / Then
        with pytest.raises(DocumentNotFoundError):
            await use_case.execute(
                project_id=project_id,
                document_id=other_project_doc.id,
                user_id=user_id,
            )

    async def test_reindex_document_download_failure_sets_error_status(
        self,
        user_id,
        project_id,
        document_id,
        project,
        document,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_indexing_service: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = project
        mock_document_repository.find_by_id.return_value = document
        mock_file_storage_service.download_file.side_effect = FileNotFoundError("missing object")
        use_case = ReindexDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            document_indexing_service=mock_document_indexing_service,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            document_id=document_id,
            user_id=user_id,
        )

        # Then
        assert mock_document_repository.save.call_count == 2
        first_saved = mock_document_repository.save.call_args_list[0].args[0]
        second_saved = mock_document_repository.save.call_args_list[1].args[0]
        assert first_saved.status == DocumentStatus.PROCESSING
        assert second_saved.status == DocumentStatus.ERROR
        assert second_saved.error_message is not None
        assert "missing object" in second_saved.error_message
        assert result.status == DocumentStatus.ERROR

    async def test_reindex_document_already_processing_does_not_raise(
        self,
        user_id,
        project_id,
        project,
        document,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_indexing_service: AsyncMock,
    ) -> None:
        # Given
        processing_document = replace(document, status=DocumentStatus.PROCESSING)
        indexed_document = replace(
            processing_document,
            status=DocumentStatus.PROCESSING,
            processing_strategy=ChunkingStrategy.FIXED_WINDOW,
        )
        mock_project_repository.find_by_id.return_value = project
        mock_document_repository.find_by_id.return_value = processing_document
        mock_document_indexing_service.run_pipeline.return_value = indexed_document
        use_case = ReindexDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            document_indexing_service=mock_document_indexing_service,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            document_id=processing_document.id,
            user_id=user_id,
        )

        # Then
        assert mock_document_repository.save.call_count == 1
        saved = mock_document_repository.save.call_args_list[0].args[0]
        assert saved.status == DocumentStatus.INDEXED
        assert result.status == DocumentStatus.INDEXED

    async def test_reindex_document_project_reindex_in_progress_raises(
        self,
        user_id,
        project_id,
        project,
        document_id,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
        mock_document_indexing_service: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = replace(
            project, reindex_status="in_progress"
        )
        use_case = ReindexDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            document_indexing_service=mock_document_indexing_service,
        )

        # When / Then
        with pytest.raises(ProjectReindexInProgressError):
            await use_case.execute(
                project_id=project_id,
                document_id=document_id,
                user_id=user_id,
            )
