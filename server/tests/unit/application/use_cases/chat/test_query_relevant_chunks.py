from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.use_cases.chat.query_relevant_chunks import QueryRelevantChunks
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class TestQueryRelevantChunks:
    @pytest.fixture
    def mock_project_repository(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def mock_embedding_service(self) -> AsyncMock:
        embedding_service = AsyncMock()
        embedding_service.embed_texts.return_value = [[0.1, 0.2, 0.3]]
        return embedding_service

    @pytest.fixture
    def mock_chunk_retrieval_service(self) -> AsyncMock:
        retrieval_service = AsyncMock()
        retrieval_service.retrieve_chunks.return_value = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="first chunk",
                score=0.92,
            ),
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=uuid4(),
                content="second chunk",
                score=0.88,
            ),
        ]
        return retrieval_service

    @pytest.fixture
    def use_case(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
        mock_chunk_retrieval_service: AsyncMock,
    ) -> QueryRelevantChunks:
        return QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_chunk_retrieval_service,
        )

    async def test_query_relevant_chunks_success(
        self,
        use_case: QueryRelevantChunks,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
        mock_chunk_retrieval_service: AsyncMock,
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

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="What is clean architecture?",
            limit=2,
        )

        # Then
        mock_embedding_service.embed_texts.assert_awaited_once_with(["What is clean architecture?"])
        mock_chunk_retrieval_service.retrieve_chunks.assert_awaited_once_with(
            project_id=project_id,
            query_text="What is clean architecture?",
            query_embedding=[0.1, 0.2, 0.3],
            limit=2,
            offset=0,
            min_score=0.0,
            strategy="hybrid",
            metadata_filters=None,
        )
        assert len(result.chunks) == 2
        assert result.chunks[0].content == "first chunk"
        assert result.strategy_used == "hybrid"
        assert result.execution_time_ms >= 0.0

    async def test_query_relevant_chunks_unknown_project_raises_error(
        self,
        use_case: QueryRelevantChunks,
        mock_project_repository: AsyncMock,
    ) -> None:
        # Given
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = None

        # When / Then
        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(
                project_id=project_id,
                user_id=uuid4(),
                query="hello",
                limit=3,
            )

    async def test_query_relevant_chunks_project_owned_by_another_user_raises_error(
        self,
        use_case: QueryRelevantChunks,
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
                user_id=uuid4(),
                query="hello",
                limit=3,
            )

    async def test_query_relevant_chunks_filters_by_min_score(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
        mock_chunk_retrieval_service: AsyncMock,
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
        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_chunk_retrieval_service,
            min_score=0.9,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="What is clean architecture?",
            limit=2,
        )

        # Then
        assert len(result.chunks) == 1
        assert result.chunks[0].content == "first chunk"

    async def test_query_relevant_chunks_passes_strategy_and_filters(
        self,
        use_case: QueryRelevantChunks,
        mock_project_repository: AsyncMock,
        mock_chunk_retrieval_service: AsyncMock,
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

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="JWT token expiration",
            limit=3,
            strategy="fulltext",
            metadata_filters={"source_type": "paragraph"},
        )

        # Then
        mock_chunk_retrieval_service.retrieve_chunks.assert_awaited_with(
            project_id=project_id,
            query_text="JWT token expiration",
            query_embedding=[0.1, 0.2, 0.3],
            limit=3,
            offset=0,
            min_score=0.0,
            strategy="fulltext",
            metadata_filters={"source_type": "paragraph"},
        )

    async def test_query_relevant_chunks_auto_strategy_resolves_to_fulltext(self) -> None:
        # Given
        project_id = uuid4()
        user_id = uuid4()
        project_repository = AsyncMock()
        project_repository.find_by_id.return_value = Project(
            id=project_id,
            user_id=user_id,
            name="Project",
            description="",
            system_prompt="",
            is_published=False,
            created_at=datetime.now(UTC),
        )
        embedding_service = AsyncMock()
        embedding_service.embed_texts.return_value = [[0.1, 0.2, 0.3]]
        retrieval_service = AsyncMock()
        retrieval_service.retrieve_chunks.return_value = []
        use_case = QueryRelevantChunks(
            project_repository=project_repository,
            embedding_service=embedding_service,
            chunk_retrieval_service=retrieval_service,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query='JWT "token"',
            strategy="auto",
        )

        # Then
        assert result.strategy_used == "fulltext"
