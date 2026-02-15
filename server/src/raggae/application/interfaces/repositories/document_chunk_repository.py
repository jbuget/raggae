from typing import Protocol
from uuid import UUID

from raggae.domain.entities.document_chunk import DocumentChunk


class DocumentChunkRepository(Protocol):
    """Interface for document chunk persistence."""

    async def save_many(self, chunks: list[DocumentChunk]) -> None: ...

    async def find_by_document_id(self, document_id: UUID) -> list[DocumentChunk]: ...

    async def delete_by_document_id(self, document_id: UUID) -> None: ...
