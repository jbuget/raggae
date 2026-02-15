from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from raggae.domain.entities.document_chunk import DocumentChunk


@dataclass
class DocumentChunkDTO:
    """Data Transfer Object for DocumentChunk."""

    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    created_at: datetime
    metadata_json: dict[str, Any] | None

    @classmethod
    def from_entity(cls, chunk: DocumentChunk) -> "DocumentChunkDTO":
        return cls(
            id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            created_at=chunk.created_at,
            metadata_json=chunk.metadata_json,
        )
