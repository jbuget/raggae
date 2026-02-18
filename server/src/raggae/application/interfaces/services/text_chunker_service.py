from typing import Protocol

from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TextChunkerService(Protocol):
    """Interface for splitting text into chunks."""

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_WINDOW,
        embedding_service: EmbeddingService | None = None,
    ) -> list[str]: ...
