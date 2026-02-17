from dataclasses import replace
from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.project.reindex_project import ReindexProject
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.document_exceptions import EmbeddingGenerationError
from raggae.domain.exceptions.project_exceptions import (
    ProjectNotFoundError,
    ProjectReindexInProgressError,
)
from raggae.domain.value_objects.document_status import DocumentStatus


class TestReindexProject:
    @pytest.fixture
    def user_id(self):
        return uuid4()

    @pytest.fixture
    def project_id(self):
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
    def document(self, project_id):
        doc_id = uuid4()
        return Document(
            id=doc_id,
            project_id=project_id,
            file_name="doc.txt",
            content_type="text/plain",
            file_size=12,
            storage_key=f"projects/{project_id}/documents/{doc_id}-doc.txt",
            created_at=datetime.now(UTC),
            status=DocumentStatus.INDEXED,
        )

    async def test_reindex_project_success(
        self,
        project_id,
        user_id,
        project,
        document,
    ) -> None:
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = project
        document_repository = AsyncMock()
        document_repository.find_by_project_id.return_value = [document]
        file_storage_service = AsyncMock()
        file_storage_service.download_file.return_value = (b"hello", "text/plain")
        indexing_service = AsyncMock()
        indexing_service.run_pipeline.return_value = replace(
            document, status=DocumentStatus.PROCESSING
        )

        use_case = ReindexProject(
            project_repository=project_repository,
            document_repository=document_repository,
            file_storage_service=file_storage_service,
            document_indexing_service=indexing_service,
        )

        result = await use_case.execute(project_id=project_id, user_id=user_id)

        assert result.project_id == project_id
        assert result.total_documents == 1
        assert result.indexed_documents == 1
        assert result.failed_documents == 0
        assert project_repository.save.await_count == 3

    async def test_reindex_project_partial_failure(
        self,
        project_id,
        user_id,
        project,
        document,
    ) -> None:
        second = replace(
            document,
            id=uuid4(),
            storage_key=f"projects/{project_id}/documents/{uuid4()}-doc2.txt",
        )
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = project
        document_repository = AsyncMock()
        document_repository.find_by_project_id.return_value = [document, second]
        file_storage_service = AsyncMock()
        file_storage_service.download_file.side_effect = [
            (b"hello", "text/plain"),
            FileNotFoundError("missing"),
        ]
        indexing_service = AsyncMock()
        indexing_service.run_pipeline.return_value = replace(
            document, status=DocumentStatus.PROCESSING
        )

        use_case = ReindexProject(
            project_repository=project_repository,
            document_repository=document_repository,
            file_storage_service=file_storage_service,
            document_indexing_service=indexing_service,
        )

        result = await use_case.execute(project_id=project_id, user_id=user_id)

        assert result.total_documents == 2
        assert result.indexed_documents == 1
        assert result.failed_documents == 1
        assert document_repository.save.await_count == 4

    async def test_reindex_project_not_found_raises(self, project_id) -> None:
        use_case = ReindexProject(
            project_repository=AsyncMock(find_by_id=AsyncMock(return_value=None)),
            document_repository=AsyncMock(),
            file_storage_service=AsyncMock(),
            document_indexing_service=AsyncMock(),
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project_id, user_id=uuid4())

    async def test_reindex_project_already_in_progress_raises(
        self, project_id, user_id, project
    ) -> None:
        in_progress = replace(project, reindex_status="in_progress")
        use_case = ReindexProject(
            project_repository=AsyncMock(find_by_id=AsyncMock(return_value=in_progress)),
            document_repository=AsyncMock(),
            file_storage_service=AsyncMock(),
            document_indexing_service=AsyncMock(),
        )

        with pytest.raises(ProjectReindexInProgressError):
            await use_case.execute(project_id=project_id, user_id=user_id)

    async def test_reindex_project_marks_document_error_on_pipeline_exception(
        self, project_id, user_id, project, document
    ) -> None:
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = project
        document_repository = AsyncMock()
        document_repository.find_by_project_id.return_value = [document]
        file_storage_service = AsyncMock()
        file_storage_service.download_file.return_value = (b"hello", "text/plain")
        indexing_service = AsyncMock()
        indexing_service.run_pipeline.side_effect = EmbeddingGenerationError("provider down")

        use_case = ReindexProject(
            project_repository=project_repository,
            document_repository=document_repository,
            file_storage_service=file_storage_service,
            document_indexing_service=indexing_service,
        )

        result = await use_case.execute(project_id=project_id, user_id=user_id)

        assert result.indexed_documents == 0
        assert result.failed_documents == 1
