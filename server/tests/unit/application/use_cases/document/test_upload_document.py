from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.document.upload_document import UploadDocument
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.document_exceptions import (
    DocumentTooLargeError,
    InvalidDocumentTypeError,
    ProjectDocumentLimitReachedError,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestUploadDocument:
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

    async def test_upload_document_success(
        self,
        use_case: UploadDocument,
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

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name="doc.pdf",
            file_content=b"content",
            content_type="application/pdf",
        )

        # Then
        assert result.project_id == project_id
        assert result.file_name == "doc.pdf"
        mock_file_storage_service.upload_file.assert_called_once()

    async def test_upload_document_project_not_found_raises_error(
        self,
        use_case: UploadDocument,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=uuid4(),
                user_id=uuid4(),
                file_name="doc.pdf",
                file_content=b"content",
                content_type="application/pdf",
            )

    async def test_upload_document_with_invalid_extension_raises_error(
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

        # When / Then
        with pytest.raises(InvalidDocumentTypeError):
            await use_case.execute(
                project_id=project_id,
                user_id=user_id,
                file_name="doc.exe",
                file_content=b"content",
                content_type="application/octet-stream",
            )

    async def test_upload_document_too_large_raises_error(
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

        # When / Then
        with pytest.raises(DocumentTooLargeError):
            await use_case.execute(
                project_id=project_id,
                user_id=user_id,
                file_name="doc.pdf",
                file_content=b"x" * (104857600 + 1),
                content_type="application/pdf",
            )

    async def test_upload_doc_format_raises_error(
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

        # When / Then
        with pytest.raises(InvalidDocumentTypeError):
            await use_case.execute(
                project_id=project_id,
                user_id=user_id,
                file_name="doc.doc",
                file_content=b"content",
                content_type="application/msword",
            )

    async def test_upload_document_quota_reached_raises_error(
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
        # Simulate 100 existing documents
        mock_document_repository.find_by_project_id.return_value = [
            Document(
                id=uuid4(),
                project_id=project_id,
                file_name=f"doc_{i}.pdf",
                content_type="application/pdf",
                file_size=100,
                storage_key=f"key_{i}",
                created_at=datetime.now(UTC),
            )
            for i in range(100)
        ]
        use_case = UploadDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
            max_file_size=104857600,
            max_documents_per_project=100,
        )

        # When / Then
        with pytest.raises(ProjectDocumentLimitReachedError):
            await use_case.execute(
                project_id=project_id,
                user_id=user_id,
                file_name="one_more.pdf",
                file_content=b"content",
                content_type="application/pdf",
            )
