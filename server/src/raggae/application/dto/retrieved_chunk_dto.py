from dataclasses import dataclass
from uuid import UUID


@dataclass
class RetrievedChunkDTO:
    """Data Transfer Object for retrieval results."""

    chunk_id: UUID
    document_id: UUID
    content: str
    score: float
