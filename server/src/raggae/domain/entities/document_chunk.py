from dataclasses import dataclass
from datetime import datetime
from typing import Any
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
    metadata_json: dict[str, Any] | None = None
