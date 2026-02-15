from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.document.delete_document import DeleteDocument
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.document_exceptions import DocumentNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestDeleteDocument:
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
    ) -> DeleteDocument:
        return DeleteDocument(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
        )

    async def test_delete_document_success(
        self,
        use_case: DeleteDocument,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        document_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Test",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_document_repository.find_by_id.return_value = Document(
            id=document_id,
            project_id=project_id,
            file_name="doc.pdf",
            content_type="application/pdf",
            file_size=100,
            storage_key="key-1",
            created_at=datetime.now(UTC),
        )

        # When
        await use_case.execute(project_id=project_id, document_id=document_id, user_id=user_id)

        # Then
        mock_file_storage_service.delete_file.assert_called_once_with("key-1")
        mock_document_repository.delete.assert_called_once_with(document_id)

    async def test_delete_document_missing_project_raises_error(
        self,
        use_case: DeleteDocument,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        mock_project_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=uuid4(), document_id=uuid4(), user_id=uuid4())

    async def test_delete_document_not_found_raises_error(
        self,
        use_case: DeleteDocument,
        mock_document_repository: AsyncMock,
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
        mock_document_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(DocumentNotFoundError):
            await use_case.execute(project_id=project_id, document_id=uuid4(), user_id=user_id)
