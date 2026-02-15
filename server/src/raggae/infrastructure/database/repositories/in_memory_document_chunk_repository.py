from uuid import UUID

from raggae.domain.entities.document_chunk import DocumentChunk


class InMemoryDocumentChunkRepository:
    """In-memory document chunk repository for testing."""

    def __init__(self) -> None:
        self._chunks: dict[UUID, DocumentChunk] = {}

    async def save_many(self, chunks: list[DocumentChunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.id] = chunk

    async def find_by_document_id(self, document_id: UUID) -> list[DocumentChunk]:
        return [chunk for chunk in self._chunks.values() if chunk.document_id == document_id]

    async def delete_by_document_id(self, document_id: UUID) -> None:
        chunk_ids = [
            chunk_id
            for chunk_id, chunk in self._chunks.items()
            if chunk.document_id == document_id
        ]
        for chunk_id in chunk_ids:
            self._chunks.pop(chunk_id, None)
