from typing import Protocol
from uuid import UUID

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


class ChunkRetrievalService(Protocol):
    """Interface for retrieving relevant chunks from a hybrid search index."""

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
        ...
