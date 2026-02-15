from math import sqrt
from uuid import UUID

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO
from raggae.application.interfaces.repositories.document_chunk_repository import (
    DocumentChunkRepository,
)
from raggae.application.interfaces.repositories.document_repository import DocumentRepository


class InMemoryChunkRetrievalService:
    """In-memory chunk retrieval based on cosine similarity."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        document_chunk_repository: DocumentChunkRepository,
    ) -> None:
        self._document_repository = document_repository
        self._document_chunk_repository = document_chunk_repository

    async def retrieve_chunks(
        self,
        project_id: UUID,
        query_embedding: list[float],
        limit: int,
        min_score: float = 0.0,
    ) -> list[RetrievedChunkDTO]:
        if limit <= 0:
            return []

        project_documents = await self._document_repository.find_by_project_id(project_id)
        retrieval_results: list[RetrievedChunkDTO] = []

        for document in project_documents:
            chunks = await self._document_chunk_repository.find_by_document_id(document.id)
            for chunk in chunks:
                score = _cosine_similarity(query_embedding, chunk.embedding)
                retrieval_results.append(
                    RetrievedChunkDTO(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        content=chunk.content,
                        score=score,
                    )
                )

        filtered_results = [chunk for chunk in retrieval_results if chunk.score >= min_score]
        filtered_results.sort(key=lambda chunk: chunk.score, reverse=True)
        return filtered_results[:limit]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot_product = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot_product / (left_norm * right_norm)
