from raggae.application.interfaces.services.text_chunker_service import TextChunkerService
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class AdaptiveTextChunkerService:
    """Routes chunking requests to the strategy-specific chunker."""

    def __init__(
        self,
        fixed_window_chunker: TextChunkerService,
        paragraph_chunker: TextChunkerService,
        heading_section_chunker: TextChunkerService,
    ) -> None:
        self._fixed_window_chunker = fixed_window_chunker
        self._paragraph_chunker = paragraph_chunker
        self._heading_section_chunker = heading_section_chunker

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_WINDOW,
    ) -> list[str]:
        if strategy == ChunkingStrategy.PARAGRAPH:
            return await self._paragraph_chunker.chunk_text(text, strategy)
        if strategy == ChunkingStrategy.HEADING_SECTION:
            return await self._heading_section_chunker.chunk_text(text, strategy)
        return await self._fixed_window_chunker.chunk_text(text, ChunkingStrategy.FIXED_WINDOW)
