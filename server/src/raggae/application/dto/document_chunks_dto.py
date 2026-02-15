from dataclasses import dataclass
from uuid import UUID

from raggae.application.dto.document_chunk_dto import DocumentChunkDTO
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


@dataclass
class DocumentChunksDTO:
    """Data Transfer Object for a document chunk listing."""

    document_id: UUID
    processing_strategy: ChunkingStrategy | None
    chunks: list[DocumentChunkDTO]
