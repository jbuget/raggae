from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.use_cases.document.list_project_documents import ListProjectDocuments
from raggae.domain.entities.document import Document
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestListProjectDocuments:
    @pytest.fixture
    def mock_document_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(
        self,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
    ) -> ListProjectDocuments:
        return ListProjectDocuments(
            document_repository=mock_document_repository,
            project_repository=mock_project_repository,
        )

    async def test_list_project_documents_success(
        self,
        use_case: ListProjectDocuments,
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
        mock_document_repository.find_by_project_id.return_value = [
            Document(
                id=uuid4(),
                project_id=project_id,
                file_name="doc1.pdf",
                content_type="application/pdf",
                file_size=100,
                storage_key="key-1",
                created_at=datetime.now(UTC),
            ),
        ]

        # When
        result = await use_case.execute(project_id=project_id, user_id=user_id)

        # Then
        assert len(result) == 1
        assert result[0].file_name == "doc1.pdf"

    async def test_list_project_documents_other_user_raises_error(
        self,
        use_case: ListProjectDocuments,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=uuid4(),
            name="Test",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(project_id=project_id, user_id=uuid4())
