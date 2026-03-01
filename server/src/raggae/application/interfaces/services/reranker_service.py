from typing import Protocol

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


class RerankerService(Protocol):
    """Interface for reranking retrieved chunks by semantic relevance."""

    async def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunkDTO],
        top_k: int,
        query_embedding: list[float] | None = None,
    ) -> list[RetrievedChunkDTO]: ...
