from typing import Protocol

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TextChunkerService(Protocol):
    """Interface for splitting text into chunks."""

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_WINDOW,
    ) -> list[str]: ...
