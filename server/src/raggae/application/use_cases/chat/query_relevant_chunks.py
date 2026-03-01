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
from raggae.application.interfaces.services.project_embedding_service_resolver import (
    ProjectEmbeddingServiceResolver,
)
from raggae.application.interfaces.services.reranker_service import RerankerService
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class QueryRelevantChunks:
    """Use Case: Retrieve relevant chunks for a user query within a project."""

    def __init__(
        self,
        project_repository: ProjectRepository,
        embedding_service: EmbeddingService,
        chunk_retrieval_service: ChunkRetrievalService,
        project_embedding_service_resolver: ProjectEmbeddingServiceResolver | None = None,
        min_score: float = 0.0,
        reranker_service: RerankerService | None = None,
        reranker_candidate_multiplier: int = 3,
        document_chunk_repository: DocumentChunkRepository | None = None,
        context_window_size: int = 0,
    ) -> None:
        self._project_repository = project_repository
        self._embedding_service = embedding_service
        self._chunk_retrieval_service = chunk_retrieval_service
        self._project_embedding_service_resolver = project_embedding_service_resolver
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
        min_score: float | None = None,
        reranker_service: RerankerService | None = None,
        reranker_candidate_multiplier: int | None = None,
        metadata_filters: dict[str, object] | None = None,
        offset: int = 0,
    ) -> QueryRelevantChunksResultDTO:
        started_at = perf_counter()
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        embedding_service = (
            self._project_embedding_service_resolver.resolve(project)
            if self._project_embedding_service_resolver is not None
            else self._embedding_service
        )
        query_embedding = (await embedding_service.embed_texts([query]))[0]
        strategy_used = _resolve_strategy(strategy, query)
        effective_min_score = self._min_score if min_score is None else min_score
        effective_reranker_service = (
            self._reranker_service if reranker_service is None else reranker_service
        )
        effective_reranker_candidate_multiplier = (
            self._reranker_candidate_multiplier
            if reranker_candidate_multiplier is None
            else reranker_candidate_multiplier
        )

        fetch_limit = (
            limit * effective_reranker_candidate_multiplier
            if effective_reranker_service
            else limit
        )

        chunks = await self._chunk_retrieval_service.retrieve_chunks(
            project_id=project_id,
            query_text=query,
            query_embedding=query_embedding,
            limit=fetch_limit,
            offset=offset,
            min_score=effective_min_score,
            strategy=strategy_used,
            metadata_filters=metadata_filters,
        )

        if effective_reranker_service is not None:
            chunks = await effective_reranker_service.rerank(
                query, chunks, top_k=limit, query_embedding=query_embedding,
            )
        else:
            chunks = [chunk for chunk in chunks if chunk.score >= effective_min_score]

        chunks = await self._expand_context_window(chunks)
        chunks = await self._resolve_parent_context(chunks)

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

        # Group chunks by document_id with their indices (skip child chunks —
        # their context comes from the parent, not from neighbors)
        doc_indices: dict[UUID, set[int]] = defaultdict(set)
        for chunk in chunks:
            if chunk.chunk_index is not None and chunk.chunk_level != "child":
                doc_indices[chunk.document_id].add(chunk.chunk_index)

        if not doc_indices:
            return chunks

        # Collect document_file_name from original chunks
        doc_file_names: dict[UUID, str | None] = {}
        for chunk in chunks:
            if chunk.document_id not in doc_file_names and chunk.document_file_name is not None:
                doc_file_names[chunk.document_id] = chunk.document_file_name

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
                        document_file_name=doc_file_names.get(nc.document_id),
                    )
                )

        # Merge and sort by (document_id, chunk_index)
        merged = list(chunks) + neighbor_dtos
        merged.sort(key=lambda c: (str(c.document_id), c.chunk_index or 0))
        return merged

    async def _resolve_parent_context(
        self, chunks: list[RetrievedChunkDTO]
    ) -> list[RetrievedChunkDTO]:
        if self._document_chunk_repository is None:
            return chunks

        from dataclasses import replace

        resolved: list[RetrievedChunkDTO] = []
        parent_cache: dict[UUID, str | None] = {}
        seen_parent_ids: set[UUID] = set()

        for chunk in chunks:
            if chunk.chunk_level == "child" and chunk.parent_chunk_id is not None:
                parent_id = chunk.parent_chunk_id

                # Deduplicate: keep only the first (highest-scored) child per parent
                if parent_id in seen_parent_ids:
                    continue
                seen_parent_ids.add(parent_id)

                if parent_id not in parent_cache:
                    parent = await self._document_chunk_repository.find_by_id(parent_id)
                    parent_cache[parent_id] = parent.content if parent else None

                parent_content = parent_cache[parent_id]
                if parent_content is not None:
                    resolved.append(replace(chunk, content=parent_content))
                else:
                    resolved.append(chunk)
            else:
                resolved.append(chunk)

        return resolved


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
