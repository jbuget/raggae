from datetime import UTC, datetime
from uuid import uuid4

from raggae.application.dto.document_chunk_dto import DocumentChunkDTO
from raggae.domain.entities.document_chunk import DocumentChunk
from raggae.domain.value_objects.chunk_level import ChunkLevel


class TestDocumentChunkDTO:
    def test_from_entity_maps_chunk_level_and_parent_chunk_id(self) -> None:
        # Given
        parent_id = uuid4()
        chunk = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=1,
            content="child content",
            embedding=[0.1, 0.2],
            created_at=datetime.now(UTC),
            chunk_level=ChunkLevel.CHILD,
            parent_chunk_id=parent_id,
        )

        # When
        dto = DocumentChunkDTO.from_entity(chunk)

        # Then
        assert dto.chunk_level == "child"
        assert dto.parent_chunk_id == parent_id

    def test_from_entity_defaults_to_standard(self) -> None:
        # Given
        chunk = DocumentChunk(
            id=uuid4(),
            document_id=uuid4(),
            chunk_index=0,
            content="standard content",
            embedding=[0.1, 0.2],
            created_at=datetime.now(UTC),
        )

        # When
        dto = DocumentChunkDTO.from_entity(chunk)

        # Then
        assert dto.chunk_level == "standard"
        assert dto.parent_chunk_id is None
