from uuid import UUID

from raggae.domain.entities.document_chunk import DocumentChunk


class InMemoryDocumentChunkRepository:
    """In-memory document chunk repository for testing."""

    def __init__(self) -> None:
        self._chunks: dict[UUID, DocumentChunk] = {}

    async def save_many(self, chunks: list[DocumentChunk]) -> None:
        for chunk in chunks:
            self._chunks[chunk.id] = chunk

    async def find_by_id(self, chunk_id: UUID) -> DocumentChunk | None:
        return self._chunks.get(chunk_id)

    async def find_by_document_id(self, document_id: UUID) -> list[DocumentChunk]:
        return [chunk for chunk in self._chunks.values() if chunk.document_id == document_id]

    async def find_by_document_id_and_indices(
        self, document_id: UUID, indices: set[int]
    ) -> list[DocumentChunk]:
        return [
            chunk
            for chunk in self._chunks.values()
            if chunk.document_id == document_id and chunk.chunk_index in indices
        ]

    async def delete_by_document_id(self, document_id: UUID) -> None:
        chunk_ids = [
            chunk_id for chunk_id, chunk in self._chunks.items() if chunk.document_id == document_id
        ]
        for chunk_id in chunk_ids:
            self._chunks.pop(chunk_id, None)
