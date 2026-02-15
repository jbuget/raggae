from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class DocumentChunk:
    """Document chunk with embedding vector."""

    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    embedding: list[float]
    created_at: datetime
