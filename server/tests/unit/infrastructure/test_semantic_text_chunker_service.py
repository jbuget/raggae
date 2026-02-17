from raggae.infrastructure.services.in_memory_embedding_service import (
    InMemoryEmbeddingService,
)
from raggae.infrastructure.services.semantic_text_chunker_service import (
    SemanticTextChunkerService,
)


class TestSemanticTextChunkerService:
    async def test_chunk_text_splits_on_semantic_break(self) -> None:
        # Given
        embedding_service = InMemoryEmbeddingService(dimension=8)
        chunker = SemanticTextChunkerService(
            embedding_service=embedding_service,
            chunk_size=300,
            chunk_overlap=20,
            similarity_threshold=0.95,
        )
        text = "Alpha domain sentence one. Alpha domain sentence two. Beta topic starts now."

        # When
        chunks = await chunker.chunk_text(text)

        # Then
        assert len(chunks) >= 1
        assert all(chunk.strip() for chunk in chunks)

    async def test_chunk_text_homogeneous_text_keeps_single_chunk(self) -> None:
        # Given
        embedding_service = InMemoryEmbeddingService(dimension=8)
        chunker = SemanticTextChunkerService(
            embedding_service=embedding_service,
            chunk_size=500,
            chunk_overlap=20,
            similarity_threshold=0.1,
        )
        text = "Sentence one. Sentence two. Sentence three."

        # When
        chunks = await chunker.chunk_text(text)

        # Then
        assert len(chunks) == 1

    async def test_chunk_text_splits_when_chunk_exceeds_max_size(self) -> None:
        # Given
        embedding_service = InMemoryEmbeddingService(dimension=8)
        chunker = SemanticTextChunkerService(
            embedding_service=embedding_service,
            chunk_size=40,
            chunk_overlap=10,
        )
        text = (
            "This sentence is intentionally very long to exceed the configured chunk size. "
            "Another long sentence follows to keep splitting active."
        )

        # When
        chunks = await chunker.chunk_text(text)

        # Then
        assert len(chunks) >= 2
        assert all(len(chunk) <= 40 for chunk in chunks)
