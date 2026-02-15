from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class SimpleTextChunkerService:
    """Simple character-based text chunker."""

    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_WINDOW,
    ) -> list[str]:
        del strategy
        normalized = text.strip()
        if not normalized:
            return []

        chunks: list[str] = []
        start = 0
        step = max(1, self._chunk_size - self._chunk_overlap)
        while start < len(normalized):
            end = start + self._chunk_size
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start += step
        return chunks
