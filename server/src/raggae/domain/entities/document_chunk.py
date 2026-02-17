from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from raggae.domain.value_objects.chunk_level import ChunkLevel


@dataclass(frozen=True)
class DocumentChunk:
    """Document chunk with embedding vector."""

    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    embedding: list[float]
    created_at: datetime
    metadata_json: dict[str, Any] | None = None
    chunk_level: ChunkLevel = ChunkLevel.STANDARD
    parent_chunk_id: UUID | None = None
