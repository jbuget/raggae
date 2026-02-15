from time import perf_counter
from uuid import UUID

from raggae.application.dto.query_relevant_chunks_result_dto import (
    QueryRelevantChunksResultDTO,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.chunk_retrieval_service import ChunkRetrievalService
from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class QueryRelevantChunks:
    """Use Case: Retrieve relevant chunks for a user query within a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        embedding_service: EmbeddingService,
        chunk_retrieval_service: ChunkRetrievalService,
        min_score: float = 0.0,
    ) -> None:
        self._project_repository = project_repository
        self._embedding_service = embedding_service
        self._chunk_retrieval_service = chunk_retrieval_service
        self._min_score = min_score

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        query: str,
        limit: int = 5,
        strategy: str = "hybrid",
        metadata_filters: dict[str, object] | None = None,
        offset: int = 0,
    ) -> QueryRelevantChunksResultDTO:
        started_at = perf_counter()
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        query_embedding = (await self._embedding_service.embed_texts([query]))[0]
        strategy_used = _resolve_strategy(strategy, query)
        chunks = await self._chunk_retrieval_service.retrieve_chunks(
            project_id=project_id,
            query_text=query,
            query_embedding=query_embedding,
            limit=limit,
            offset=offset,
            min_score=self._min_score,
            strategy=strategy_used,
            metadata_filters=metadata_filters,
        )
        filtered_chunks = [chunk for chunk in chunks if chunk.score >= self._min_score]
        return QueryRelevantChunksResultDTO(
            chunks=filtered_chunks,
            strategy_used=strategy_used,
            execution_time_ms=(perf_counter() - started_at) * 1000.0,
        )


def _resolve_strategy(strategy: str, query_text: str) -> str:
    if strategy != "auto":
        return strategy
    has_quotes = '"' in query_text
    is_technical = any(character in query_text for character in ("_", "-")) or any(
        token.isupper() and len(token) > 1 for token in query_text.split()
    )
    is_short = len(query_text.split()) <= 3
    if has_quotes or (is_technical and is_short):
        return "fulltext"
    return "hybrid"
