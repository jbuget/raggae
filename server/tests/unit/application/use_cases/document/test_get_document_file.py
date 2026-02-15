from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.document.get_document_file import GetDocumentFile
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.document_exceptions import DocumentNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestGetDocumentFile:
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
    ) -> GetDocumentFile:
        return GetDocumentFile(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
            file_storage_service=mock_file_storage_service,
        )

    async def test_get_document_file_success(
        self,
        use_case: GetDocumentFile,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
        mock_file_storage_service: AsyncMock,
    ) -> None:
        user_id = uuid4()
        project_id = uuid4()
        document_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        mock_document_repository.find_by_id.return_value = Document(
            id=document_id,
            project_id=project_id,
            file_name="doc.txt",
            content_type="text/plain",
            file_size=10,
            storage_key="projects/x/documents/y-doc.txt",
            created_at=datetime.now(UTC),
        )
        mock_file_storage_service.download_file.return_value = (b"hello", "text/plain")

        result = await use_case.execute(project_id=project_id, document_id=document_id, user_id=user_id)

        assert result.document_id == document_id
        assert result.file_name == "doc.txt"
        assert result.content_type == "text/plain"
        assert result.content == b"hello"

    async def test_get_document_file_other_user_project_raises_error(
        self,
        use_case: GetDocumentFile,
        mock_project_repository: AsyncMock,
    ) -> None:
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=uuid4(),
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project_id, document_id=uuid4(), user_id=uuid4())

    async def test_get_document_file_not_in_project_raises_error(
        self,
        use_case: GetDocumentFile,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
    ) -> None:
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
        mock_document_repository.find_by_id.return_value = Document(
            id=uuid4(),
            project_id=uuid4(),
            file_name="doc.txt",
            content_type="text/plain",
            file_size=12,
            storage_key="documents/doc.txt",
            created_at=datetime.now(UTC),
        )

        with pytest.raises(DocumentNotFoundError):
            await use_case.execute(project_id=project_id, document_id=uuid4(), user_id=user_id)
