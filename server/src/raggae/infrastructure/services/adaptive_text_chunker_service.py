from raggae.application.interfaces.services.text_chunker_service import TextChunkerService
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class AdaptiveTextChunkerService:
    """Routes chunking requests to the strategy-specific chunker."""

    def __init__(
        self,
        fixed_window_chunker: TextChunkerService,
        paragraph_chunker: TextChunkerService,
        heading_section_chunker: TextChunkerService,
        semantic_chunker: TextChunkerService | None = None,
        context_window_size: int = 0,
    ) -> None:
        self._fixed_window_chunker = fixed_window_chunker
        self._paragraph_chunker = paragraph_chunker
        self._heading_section_chunker = heading_section_chunker
        self._semantic_chunker = semantic_chunker
        self._context_window_size = max(0, context_window_size)

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_WINDOW,
    ) -> list[str]:
        if strategy == ChunkingStrategy.PARAGRAPH:
            chunks = await self._paragraph_chunker.chunk_text(text, strategy)
            return self._apply_context_window(chunks)
        if strategy == ChunkingStrategy.HEADING_SECTION:
            chunks = await self._heading_section_chunker.chunk_text(text, strategy)
            return self._apply_context_window(chunks)
        if strategy == ChunkingStrategy.SEMANTIC and self._semantic_chunker is not None:
            chunks = await self._semantic_chunker.chunk_text(text, strategy)
            return self._apply_context_window(chunks)
        return await self._fixed_window_chunker.chunk_text(text, ChunkingStrategy.FIXED_WINDOW)

    def _apply_context_window(self, chunks: list[str]) -> list[str]:
        if self._context_window_size == 0 or len(chunks) <= 1:
            return chunks

        contextualized = [chunks[0]]
        for index in range(1, len(chunks)):
            previous_tail = chunks[index - 1][-self._context_window_size :].strip()
            current = chunks[index].strip()
            if previous_tail:
                contextualized.append(f"{previous_tail}\n\n{current}")
            else:
                contextualized.append(current)
        return contextualized
