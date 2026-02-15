from __future__ import annotations

from collections import defaultdict
from time import perf_counter
from uuid import UUID

from raggae.application.dto.query_relevant_chunks_result_dto import (
    QueryRelevantChunksResultDTO,
)
from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.services.chunk_retrieval_service import ChunkRetrievalService
from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.application.interfaces.services.reranker_service import RerankerService
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class QueryRelevantChunks:
    """Use Case: Retrieve relevant chunks for a user query within a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        embedding_service: EmbeddingService,
        chunk_retrieval_service: ChunkRetrievalService,
        min_score: float = 0.0,
        reranker_service: RerankerService | None = None,
        reranker_candidate_multiplier: int = 3,
        document_chunk_repository: DocumentChunkRepository | None = None,
        context_window_size: int = 0,
    ) -> None:
        self._project_repository = project_repository
        self._embedding_service = embedding_service
        self._chunk_retrieval_service = chunk_retrieval_service
        self._min_score = min_score
        self._reranker_service = reranker_service
        self._reranker_candidate_multiplier = reranker_candidate_multiplier
        self._document_chunk_repository = document_chunk_repository
        self._context_window_size = context_window_size

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

        fetch_limit = (
            limit * self._reranker_candidate_multiplier if self._reranker_service else limit
        )

        chunks = await self._chunk_retrieval_service.retrieve_chunks(
            project_id=project_id,
            query_text=query,
            query_embedding=query_embedding,
            limit=fetch_limit,
            offset=offset,
            min_score=self._min_score,
            strategy=strategy_used,
            metadata_filters=metadata_filters,
        )

        if self._reranker_service is not None:
            chunks = await self._reranker_service.rerank(query, chunks, top_k=limit)
        else:
            chunks = [chunk for chunk in chunks if chunk.score >= self._min_score]

        chunks = await self._expand_context_window(chunks)

        return QueryRelevantChunksResultDTO(
            chunks=chunks,
            strategy_used=strategy_used,
            execution_time_ms=(perf_counter() - started_at) * 1000.0,
        )

    async def _expand_context_window(
        self, chunks: list[RetrievedChunkDTO]
    ) -> list[RetrievedChunkDTO]:
        if self._context_window_size <= 0 or self._document_chunk_repository is None:
            return chunks

        # Group chunks by document_id with their indices
        doc_indices: dict[UUID, set[int]] = defaultdict(set)
        for chunk in chunks:
            if chunk.chunk_index is not None:
                doc_indices[chunk.document_id].add(chunk.chunk_index)

        if not doc_indices:
            return chunks

        # Compute needed neighbor indices per document
        doc_needed: dict[UUID, set[int]] = {}
        for doc_id, original_indices in doc_indices.items():
            all_indices: set[int] = set()
            for idx in original_indices:
                for offset in range(-self._context_window_size, self._context_window_size + 1):
                    neighbor = idx + offset
                    if neighbor >= 0:
                        all_indices.add(neighbor)
            missing = all_indices - original_indices
            if missing:
                doc_needed[doc_id] = missing

        # Fetch missing neighbor chunks
        neighbor_dtos: list[RetrievedChunkDTO] = []
        for doc_id, missing_indices in doc_needed.items():
            neighbor_chunks = await self._document_chunk_repository.find_by_document_id_and_indices(
                document_id=doc_id, indices=missing_indices
            )
            for nc in neighbor_chunks:
                neighbor_dtos.append(
                    RetrievedChunkDTO(
                        chunk_id=nc.id,
                        document_id=nc.document_id,
                        content=nc.content,
                        score=0.0,
                        chunk_index=nc.chunk_index,
                    )
                )

        # Merge and sort by (document_id, chunk_index)
        merged = list(chunks) + neighbor_dtos
        merged.sort(key=lambda c: (str(c.document_id), c.chunk_index or 0))
        return merged


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
