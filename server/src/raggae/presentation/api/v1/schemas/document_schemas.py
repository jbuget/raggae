from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class DocumentResponse(BaseModel):
    id: UUID
    project_id: UUID
    file_name: str
    content_type: str
    file_size: int
    created_at: datetime
    processing_strategy: ChunkingStrategy | None


class DocumentChunkResponse(BaseModel):
    id: UUID
    document_id: UUID
    chunk_index: int
    content: str
    created_at: datetime
    metadata_json: dict[str, Any] | None


class DocumentChunksResponse(BaseModel):
    document_id: UUID
    processing_strategy: ChunkingStrategy | None
    chunks: list[DocumentChunkResponse]
