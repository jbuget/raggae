from typing import Protocol
from uuid import UUID

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


class ChunkRetrievalService(Protocol):
    """Interface for retrieving relevant chunks from a vector index."""

    async def retrieve_chunks(
        self,
        project_id: UUID,
        query_embedding: list[float],
        limit: int,
        min_score: float = 0.0,
    ) -> list[RetrievedChunkDTO]: ...
