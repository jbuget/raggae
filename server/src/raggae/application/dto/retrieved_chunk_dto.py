from dataclasses import dataclass
from uuid import UUID


@dataclass
class RetrievedChunkDTO:
    """Data Transfer Object for retrieval results."""

    chunk_id: UUID
    document_id: UUID
    content: str
    score: float
    chunk_index: int | None = None
    document_file_name: str | None = None
    vector_score: float | None = None
    fulltext_score: float | None = None
