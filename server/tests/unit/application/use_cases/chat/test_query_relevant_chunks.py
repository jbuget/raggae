from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.use_cases.chat.query_relevant_chunks import QueryRelevantChunks
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


def _make_project(project_id=None, user_id=None):
    return Project(
        id=project_id or uuid4(),
        user_id=user_id or uuid4(),
        name="Project",
        description="",
        system_prompt="",
        is_published=False,
        created_at=datetime.now(UTC),
    )


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
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

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
        mock_project_repository.find_by_id.return_value = _make_project(project_id)

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
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)
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
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

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
        project_repository.find_by_id.return_value = _make_project(project_id, user_id)
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

    async def test_query_with_reranker_overfetches_and_reranks(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        raw_chunks = [
            RetrievedChunkDTO(
                chunk_id=uuid4(), document_id=uuid4(), content=f"chunk {i}", score=0.5
            )
            for i in range(6)
        ]
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_chunks.return_value = raw_chunks

        reranked = [
            RetrievedChunkDTO(
                chunk_id=raw_chunks[1].chunk_id,
                document_id=raw_chunks[1].document_id,
                content="chunk 1",
                score=0.95,
            ),
            RetrievedChunkDTO(
                chunk_id=raw_chunks[3].chunk_id,
                document_id=raw_chunks[3].document_id,
                content="chunk 3",
                score=0.80,
            ),
        ]
        mock_reranker = AsyncMock()
        mock_reranker.rerank.return_value = reranked

        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_retrieval,
            reranker_service=mock_reranker,
            reranker_candidate_multiplier=3,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test query",
            limit=2,
        )

        # Then — retrieve_chunks called with limit * multiplier
        mock_retrieval.retrieve_chunks.assert_awaited_once()
        call_kwargs = mock_retrieval.retrieve_chunks.call_args.kwargs
        assert call_kwargs["limit"] == 6  # 2 * 3

        # reranker called with original limit as top_k
        mock_reranker.rerank.assert_awaited_once_with("test query", raw_chunks, top_k=2)

        # result contains reranked chunks
        assert len(result.chunks) == 2
        assert result.chunks[0].score == pytest.approx(0.95)

    async def test_query_with_reranker_skips_min_score_filter(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_chunks.return_value = [
            RetrievedChunkDTO(chunk_id=uuid4(), document_id=uuid4(), content="relevant", score=0.5),
            RetrievedChunkDTO(
                chunk_id=uuid4(), document_id=uuid4(), content="low score", score=0.5
            ),
        ]

        mock_reranker = AsyncMock()
        mock_reranker.rerank.return_value = [
            RetrievedChunkDTO(chunk_id=uuid4(), document_id=uuid4(), content="relevant", score=0.8),
            RetrievedChunkDTO(
                chunk_id=uuid4(), document_id=uuid4(), content="low score", score=0.1
            ),
        ]

        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_retrieval,
            min_score=0.5,
            reranker_service=mock_reranker,
            reranker_candidate_multiplier=2,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test",
            limit=5,
        )

        # Then — reranker handles ranking via top_k, no post-filter on score
        assert len(result.chunks) == 2

    async def test_query_without_reranker_does_not_overfetch(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
        mock_chunk_retrieval_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_chunk_retrieval_service,
            reranker_service=None,
        )

        # When
        await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test",
            limit=5,
        )

        # Then — limit passed as-is (no multiplication)
        call_kwargs = mock_chunk_retrieval_service.retrieve_chunks.call_args.kwargs
        assert call_kwargs["limit"] == 5

    async def test_query_expands_context_window_with_neighbors(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        doc_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        retrieved = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=doc_id,
                content="chunk 2",
                score=0.9,
                chunk_index=2,
            ),
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=doc_id,
                content="chunk 5",
                score=0.8,
                chunk_index=5,
            ),
        ]
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_chunks.return_value = retrieved

        neighbor_chunks = [
            DocumentChunk(
                id=uuid4(),
                document_id=doc_id,
                chunk_index=i,
                content=f"chunk {i}",
                embedding=[],
                created_at=datetime.now(UTC),
            )
            for i in [1, 3, 4, 6]
        ]
        mock_chunk_repo = AsyncMock()
        mock_chunk_repo.find_by_document_id_and_indices.return_value = neighbor_chunks

        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_retrieval,
            document_chunk_repository=mock_chunk_repo,
            context_window_size=1,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test",
            limit=10,
        )

        # Then — chunks 1,2,3,4,5,6 present, sorted by (document_id, chunk_index)
        indices = [c.chunk_index for c in result.chunks]
        assert indices == [1, 2, 3, 4, 5, 6]

    async def test_query_no_expansion_when_window_is_zero(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
        mock_chunk_retrieval_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        mock_chunk_repo = AsyncMock()
        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_chunk_retrieval_service,
            document_chunk_repository=mock_chunk_repo,
            context_window_size=0,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test",
            limit=5,
        )

        # Then — no expansion, repository not called
        mock_chunk_repo.find_by_document_id_and_indices.assert_not_awaited()
        assert len(result.chunks) == 2

    async def test_query_deduplicates_overlapping_windows(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given — chunks 3 and 4 retrieved, window=1 → need 2,3,4,5
        user_id = uuid4()
        project_id = uuid4()
        doc_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        retrieved = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=doc_id,
                content="chunk 3",
                score=0.9,
                chunk_index=3,
            ),
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=doc_id,
                content="chunk 4",
                score=0.8,
                chunk_index=4,
            ),
        ]
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_chunks.return_value = retrieved

        # Only indices 2 and 5 are missing (3 and 4 already present)
        neighbor_chunks = [
            DocumentChunk(
                id=uuid4(),
                document_id=doc_id,
                chunk_index=i,
                content=f"chunk {i}",
                embedding=[],
                created_at=datetime.now(UTC),
            )
            for i in [2, 5]
        ]
        mock_chunk_repo = AsyncMock()
        mock_chunk_repo.find_by_document_id_and_indices.return_value = neighbor_chunks

        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_retrieval,
            document_chunk_repository=mock_chunk_repo,
            context_window_size=1,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test",
            limit=10,
        )

        # Then — 4 unique chunks, no duplicates
        indices = [c.chunk_index for c in result.chunks]
        assert indices == [2, 3, 4, 5]

        # Repository called with only the missing indices {2, 5}
        call_args = mock_chunk_repo.find_by_document_id_and_indices.call_args
        assert call_args.kwargs["indices"] == {2, 5}

    async def test_query_expansion_clamps_index_to_zero(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given — chunk 0 retrieved, window=1 → need {0, 1}, no negative
        user_id = uuid4()
        project_id = uuid4()
        doc_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        retrieved = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=doc_id,
                content="chunk 0",
                score=0.9,
                chunk_index=0,
            ),
        ]
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_chunks.return_value = retrieved

        neighbor_chunks = [
            DocumentChunk(
                id=uuid4(),
                document_id=doc_id,
                chunk_index=1,
                content="chunk 1",
                embedding=[],
                created_at=datetime.now(UTC),
            ),
        ]
        mock_chunk_repo = AsyncMock()
        mock_chunk_repo.find_by_document_id_and_indices.return_value = neighbor_chunks

        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_retrieval,
            document_chunk_repository=mock_chunk_repo,
            context_window_size=1,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test",
            limit=10,
        )

        # Then
        indices = [c.chunk_index for c in result.chunks]
        assert indices == [0, 1]

        # Only index 1 requested (0 already present, no negative indices)
        call_args = mock_chunk_repo.find_by_document_id_and_indices.call_args
        assert call_args.kwargs["indices"] == {1}

    async def test_query_expansion_preserves_original_scores(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        doc_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        retrieved = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=doc_id,
                content="chunk 2",
                score=0.95,
                chunk_index=2,
            ),
        ]
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_chunks.return_value = retrieved

        neighbor_chunks = [
            DocumentChunk(
                id=uuid4(),
                document_id=doc_id,
                chunk_index=i,
                content=f"chunk {i}",
                embedding=[],
                created_at=datetime.now(UTC),
            )
            for i in [1, 3]
        ]
        mock_chunk_repo = AsyncMock()
        mock_chunk_repo.find_by_document_id_and_indices.return_value = neighbor_chunks

        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_retrieval,
            document_chunk_repository=mock_chunk_repo,
            context_window_size=1,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test",
            limit=10,
        )

        # Then — original chunk keeps its score, neighbors get 0.0
        scores_by_index = {c.chunk_index: c.score for c in result.chunks}
        assert scores_by_index[2] == pytest.approx(0.95)
        assert scores_by_index[1] == pytest.approx(0.0)
        assert scores_by_index[3] == pytest.approx(0.0)

    async def test_query_expansion_propagates_document_file_name_to_neighbors(
        self,
        mock_project_repository: AsyncMock,
        mock_embedding_service: AsyncMock,
    ) -> None:
        # Given
        user_id = uuid4()
        project_id = uuid4()
        doc_id = uuid4()
        mock_project_repository.find_by_id.return_value = _make_project(project_id, user_id)

        retrieved = [
            RetrievedChunkDTO(
                chunk_id=uuid4(),
                document_id=doc_id,
                content="chunk 2",
                score=0.9,
                chunk_index=2,
                document_file_name="report.pdf",
            ),
        ]
        mock_retrieval = AsyncMock()
        mock_retrieval.retrieve_chunks.return_value = retrieved

        neighbor_chunks = [
            DocumentChunk(
                id=uuid4(),
                document_id=doc_id,
                chunk_index=i,
                content=f"chunk {i}",
                embedding=[],
                created_at=datetime.now(UTC),
            )
            for i in [1, 3]
        ]
        mock_chunk_repo = AsyncMock()
        mock_chunk_repo.find_by_document_id_and_indices.return_value = neighbor_chunks

        use_case = QueryRelevantChunks(
            project_repository=mock_project_repository,
            embedding_service=mock_embedding_service,
            chunk_retrieval_service=mock_retrieval,
            document_chunk_repository=mock_chunk_repo,
            context_window_size=1,
        )

        # When
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query="test",
            limit=10,
        )

        # Then — all chunks (original + neighbors) have the document_file_name
        for chunk in result.chunks:
            assert chunk.document_file_name == "report.pdf"
