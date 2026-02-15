from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.document.list_document_chunks import ListDocumentChunks
from raggae.domain.entities.document import Document
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.document_exceptions import DocumentNotFoundError
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestListDocumentChunks:
    @pytest.fixture
    def mock_document_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_document_chunk_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def use_case(
        self,
        mock_document_repository: AsyncMock,
        mock_document_chunk_repository: AsyncMock,
        mock_project_repository: AsyncMock,
    ) -> ListDocumentChunks:
        return ListDocumentChunks(
            document_repository=mock_document_repository,
            document_chunk_repository=mock_document_chunk_repository,
            project_repository=mock_project_repository,
        )

    async def test_list_document_chunks_success(
        self,
        use_case: ListDocumentChunks,
        mock_document_repository: AsyncMock,
        mock_document_chunk_repository: AsyncMock,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
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
            file_size=12,
            storage_key="documents/doc.txt",
            created_at=datetime.now(UTC),
            processing_strategy=ChunkingStrategy.FIXED_WINDOW,
        )
        mock_document_chunk_repository.find_by_document_id.return_value = [
            DocumentChunk(
                id=uuid4(),
                document_id=document_id,
                chunk_index=0,
                content="chunk-0",
                embedding=[0.1, 0.2],
                created_at=datetime.now(UTC),
            ),
            DocumentChunk(
                id=uuid4(),
                document_id=document_id,
                chunk_index=1,
                content="chunk-1",
                embedding=[0.3, 0.4],
                created_at=datetime.now(UTC),
            ),
        ]

        # When
        result = await use_case.execute(
            project_id=project_id,
            document_id=document_id,
            user_id=user_id,
        )

        # Then
        assert result.document_id == document_id
        assert result.processing_strategy == ChunkingStrategy.FIXED_WINDOW
        assert len(result.chunks) == 2
        assert result.chunks[0].chunk_index == 0
        assert result.chunks[0].content == "chunk-0"
        assert result.chunks[1].chunk_index == 1
        assert result.chunks[1].content == "chunk-1"

    async def test_list_document_chunks_other_user_project_raises_error(
        self,
        use_case: ListDocumentChunks,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
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

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project_id,
                document_id=uuid4(),
                user_id=uuid4(),
            )

    async def test_list_document_chunks_document_not_in_project_raises_error(
        self,
        use_case: ListDocumentChunks,
        mock_document_repository: AsyncMock,
        mock_project_repository: AsyncMock,
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
        mock_document_repository.find_by_id.return_value = Document(
            id=uuid4(),
            project_id=uuid4(),
            file_name="doc.txt",
            content_type="text/plain",
            file_size=12,
            storage_key="documents/doc.txt",
            created_at=datetime.now(UTC),
        )

        # When / Then
        with pytest.raises(DocumentNotFoundError):
            await use_case.execute(
                project_id=project_id,
                document_id=uuid4(),
                user_id=user_id,
            )
