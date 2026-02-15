from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


@dataclass(frozen=True)
class Document:
    """Document domain entity."""

    id: UUID
    project_id: UUID
    file_name: str
    content_type: str
    file_size: int
    storage_key: str
    created_at: datetime
    processing_strategy: ChunkingStrategy | None = None
