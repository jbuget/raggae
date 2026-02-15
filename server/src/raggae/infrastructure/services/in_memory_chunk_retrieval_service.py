from math import sqrt
from uuid import UUID

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import DocumentRepository


class InMemoryChunkRetrievalService:
    """In-memory chunk retrieval based on hybrid vector and lexical scoring."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        document_chunk_repository: DocumentChunkRepository,
        vector_weight: float = 0.6,
        fulltext_weight: float = 0.4,
    ) -> None:
        self._document_repository = document_repository
        self._document_chunk_repository = document_chunk_repository
        self._vector_weight = vector_weight
        self._fulltext_weight = fulltext_weight

    async def retrieve_chunks(
        self,
        project_id: UUID,
        query_text: str,
        query_embedding: list[float],
        limit: int,
        offset: int = 0,
        min_score: float = 0.0,
        strategy: str = "hybrid",
        metadata_filters: dict[str, object] | None = None,
    ) -> list[RetrievedChunkDTO]:
        if limit <= 0:
            return []

        project_documents = await self._document_repository.find_by_project_id(project_id)
        retrieval_results: list[RetrievedChunkDTO] = []
        query_terms = _tokenize(query_text)
        resolved_strategy = _resolve_strategy(strategy, query_text)
        vector_weight, fulltext_weight = self._weights_for_strategy(resolved_strategy)

        for document in project_documents:
            chunks = await self._document_chunk_repository.find_by_document_id(document.id)
            for chunk in chunks:
                if not _matches_filters(chunk.metadata_json, metadata_filters):
                    continue
                vector_score = _cosine_similarity(query_embedding, chunk.embedding)
                fulltext_score = _lexical_overlap_score(query_terms, chunk.content)
                score = vector_weight * vector_score + fulltext_weight * fulltext_score
                retrieval_results.append(
                    RetrievedChunkDTO(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        content=chunk.content,
                        score=score,
                        chunk_index=chunk.chunk_index,
                        document_file_name=document.file_name,
                        vector_score=vector_score,
                        fulltext_score=fulltext_score,
                    )
                )

        filtered_results = [chunk for chunk in retrieval_results if chunk.score >= min_score]
        filtered_results.sort(key=lambda chunk: chunk.score, reverse=True)
        return filtered_results[offset : offset + limit]

    def _weights_for_strategy(self, strategy: str) -> tuple[float, float]:
        if strategy == "vector":
            return 1.0, 0.0
        if strategy == "fulltext":
            return 0.0, 1.0
        return self._vector_weight, self._fulltext_weight


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot_product = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot_product / (left_norm * right_norm)


def _tokenize(text: str) -> set[str]:
    return {part.strip().lower() for part in text.split() if part.strip()}


def _lexical_overlap_score(query_terms: set[str], content: str) -> float:
    if not query_terms:
        return 0.0
    content_terms = _tokenize(content)
    if not content_terms:
        return 0.0
    overlap = len(query_terms.intersection(content_terms))
    return overlap / len(query_terms)


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


def _matches_filters(
    metadata: dict[str, object] | None,
    filters: dict[str, object] | None,
) -> bool:
    if not filters:
        return True
    payload = metadata or {}
    for key, expected in filters.items():
        current = payload.get(key)
        if isinstance(expected, list):
            if isinstance(current, list):
                if not any(item in current for item in expected):
                    return False
            elif current not in expected:
                return False
            continue
        if current != expected:
            return False
    return True
